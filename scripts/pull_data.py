import os
import numpy as np
import pandas as pd
import multiprocessing as mp
from reo.models import ErrorModel, BadPost, MessageModel, ElectricTariffModel,ScenarioModel
import datetime
import pytz
import copy

recent_interval_days = 7

def harmonize_traceback_lookups(urdb_results,error_results):
	common_lookup = copy.deepcopy(urdb_results['traceback_lookup'])
	
	for tb_id, tb in copy.deepcopy(error_results['traceback_lookup'].items()):
		stats = copy.deepcopy(error_results['traceback'][tb_id])
		
		del error_results['traceback'][tb_id]
		
		if tb in common_lookup.values():
			new_id = [k for k,v in common_lookup.items() if v==tb][0]
		else:
			if len(common_lookup.keys())==0:
				new_id = 0
			else:
				new_id = max(common_lookup.keys()) + 1
			common_lookup[new_id] = tb
		
		error_results['traceback'][new_id] = stats
	
	del urdb_results['traceback_lookup'] 
	del error_results['traceback_lookup']
	
	return urdb_results,error_results,common_lookup

def process_bad_post_set(bp_set):
	result = {}
	for bp in bp_set:
		error = str(eval(bp.__dict__['errors'])['input_errors'])
		if error not in result.keys():
			result[error[0:100]] = {'count':1,'run_uuids':[bp.__dict__['run_uuid']]}
		else:
			result[error[0:100]]['count'] += 1
			result[error[0:100]]['run_uuids'].append(bp.__dict__['run_uuid'])
	return result
	
def combine_bad_post_summaries(bp_summaries):
	result ={}
	for s in bp_summaries:
		for k,v in s.items():
			if k not in result.keys():
				result[k] = v
			else:
				for kk,vv in v.items():
					result[k][kk] += vv

	return result

def process_error_set(e_set):
	if len(e_set) == 0:
		return None
	
	result = {}
	traceback_lookup = {}
	now = datetime.datetime.utcnow()
	now = now.replace(tzinfo=pytz.utc)

	for e in e_set:
		
		e_traceback = e.traceback.replace(str(e.run_uuid), '<run_uuid>')
		if e_traceback not in traceback_lookup.values():
			tb_id = len(traceback_lookup.keys())
			traceback_lookup[tb_id] = e_traceback
		else:
			tb_id = [k for k,v in traceback_lookup.items() if v==e_traceback][0] 
		
		for n in ['task','name','message', 'traceback']:
			
			if n not in result.keys():
				result[n] = {}
			
			if n == 'message':
				 e.message = e.message.replace(e.run_uuid,'<run_uuid>')

			attr =  getattr(e,n)
			if n == 'traceback':
				attr = tb_id

			if attr in result[n].keys():
				result[n][attr]['count'] += 1
				if e.created > result[n][attr]['most_recent']:
					result[n][attr]['most_recent'] = e.created
			else:
				result[n][attr] = {'count_new'.format(recent_interval_days):0, 'count':1, 'most_recent': e.created, 'run_uuids_new':[],'run_uuids_old': []}

			if (e.created - now).seconds / (60*60*24.0) < recent_interval_days:
				result[n][attr]['count_new'] +=1
				result[n][attr]['run_uuids_new'].append(e.run_uuid)
			else:
				result[n][attr]['run_uuids_old'].append(e.run_uuid)
	result['traceback_lookup'] = traceback_lookup
	return result

def combine_error_summaries(error_summaries):

	result = {'traceback_lookup':{}}
	tb_recode = {}
	for i, es in enumerate(error_summaries):
		if es is not None:
			tb_recode[i] = {}
			for tb_id, tb in es['traceback_lookup'].items():
				if tb in result['traceback_lookup'].values():
					tb_recode[i][tb_id] = [k for k,v in result['traceback_lookup'].items() if v==tb][0]
				else:
					if tb_id not in result['traceback_lookup'].keys():
						new_tb_id = tb_id
						
					else:
						if len(result['traceback_lookup'].keys()) ==0:
							new_tb_id =0
						else:
							new_tb_id = max(result['traceback_lookup'].keys()) +1
						
						
					tb_recode[i][tb_id] = new_tb_id
					result['traceback_lookup'][new_tb_id] = tb
			del es['traceback_lookup']
				
	
	for i,es in enumerate(error_summaries):		
		if es is not None:
			for error_type in es.keys():
				if error_type != 'traceback_lookup':
					if error_type not in result.keys():
						result[error_type] = copy.deepcopy(es[error_type])
					else:
						for error_type_id in es[error_type].keys():
							if error_type == 'traceback':
								value =  copy.deepcopy(es[error_type][error_type_id])
								new_error_type_id = tb_recode[i][error_type_id]
								del  es[error_type][error_type_id]
								error_type_id = new_error_type_id
								es[error_type][error_type_id] = value
							
							if error_type_id not in result[error_type].keys():
								result[error_type][error_type_id] = copy.deepcopy(es[error_type][error_type_id])
							else:
								for attr_name, attr in es[error_type][error_type_id].items():
									if attr_name.startswith('count'):
										if attr_name in result[error_type][error_type_id].keys():
											result[error_type][error_type_id][attr_name] += attr
										else:
											result[error_type][error_type_id][attr_name] = attr
									elif attr_name == 'most_recent':
										if result[error_type][error_type_id][attr_name] < attr:
											result[error_type][error_type_id][attr_name] = attr
									else:	
										result[error_type][error_type_id][attr_name]+=attr
	return result


def process_urdb_set(urdb_set):
	if len(urdb_set) == 0:
		return None
	
	result = {"count_none":0,"count":0,'count_errors':0}
	for u in urdb_set:
		result['count'] += 1
		label = u[0] or u[1]['label'] or None
		if label == None:
			result['count_none'] += 1
		else:
			if label in result.keys():
				result[label].append(str(u[2]))
			else:
				result[label] = [str(u[2])]


	for k,v in result.items():
		if not k.startswith('count'):
			e_set = [i for i in ErrorModel.objects.filter(run_uuid__in=v)]
			result[k] = process_error_set(e_set) or {}
			result[k]['count_total']=len(v)
			result[k]['count_errors']= len(e_set)
			result['count_errors']+=len(e_set)
	return result

def combine_urdb_summaries(urdb_rates):
	result = {'traceback_lookup':{}}
	tb_recode = {}
	for u in urdb_rates:
		if u is not None:
			for rate, rate_stats in u.items():
				if not rate.startswith('count'):
					if 'traceback_lookup' in rate_stats.keys():
						tb_recode[rate] = {}
						for tb_id, tb in rate_stats['traceback_lookup'].items():
							if tb in result['traceback_lookup'].values():
								tb_recode[rate][tb_id] = [k for k,v in result['traceback_lookup'].items() if v==tb][0]
							else:
								new_tb_id = len(result['traceback_lookup']) 
								result['traceback_lookup'][new_tb_id] = tb
								tb_recode[rate][tb_id] = new_tb_id
						del rate_stats['traceback_lookup']
	for u in urdb_rates:		
		if u is not None:
			for rate, rate_stats in u.items():
				if not rate.startswith('count'):
					if 'traceback' in rate_stats.keys():
						new_traceback_data = {}
						for tb_id,tb_info in rate_stats['traceback'].items():
							new_traceback_data[tb_recode[rate][tb_id]] = tb_info
						rate_stats['traceback'] = new_traceback_data
						del new_traceback_data

					if rate not in result.keys():
						result[rate] = copy.deepcopy(u[rate])
					else:
						for k,v in rate_stats.items():
							if type(v)==int:
								if k in result[rate].keys():
									 result[rate][k] += v
								else:
									result[rate][k] = v
							else:
								if k not in result[rate].keys():
									result[rate][k] = copy.deepcopy(v)
								else:
									for sub_group, sub_group_data in v.items():
										for attr_name, attr in sub_group_data.items():
											if attr_name.startswith('count'):
												if attr_name in result[rate][k][sub_group].keys():
													result[rate][k][sub_group][attr_name] += attr
												else:
													result[rate][k][sub_group][attr_name] = attr
											elif attr_name == 'most_recent':
												if result[rate][k][sub_group][attr_name] < attr:
													result[rate][k][sub_group][attr_name] = attr
											else:
												result[rate][k][sub_group][attr_name]+=attr
				else:

					if rate in result.keys():
						result[rate] += rate_stats
					else:
						result[rate] = rate_stats
	return result

def run(*args):
	CORES = 6
	
	if 'pull_data' not in globals().values():
		p = mp.Pool(processes=CORES)	

		print ScenarioModel.objects.all().count()
		
		urdb_sets = np.array_split(np.array(ElectricTariffModel.objects.values_list("urdb_label","urdb_response","run_uuid").all()),CORES)
		urdb_results = combine_urdb_summaries(p.map(process_urdb_set, urdb_sets))

		error_sets = np.array_split(np.array(ErrorModel.objects.all()),CORES)
		error_results = combine_error_summaries(p.map(process_error_set, error_sets))

		urdb_results,error_results, common_lookup = harmonize_traceback_lookups(urdb_results,error_results)

		with open('urdb_results.txt','w+') as output_file:
			output_file.write(str(urdb_results))

		with open('error_results.txt','w+') as output_file:
			output_file.write(str(error_results))

		with open('common_lookup.txt','w+') as output_file:
			output_file.write(str(common_lookup))

		badpost_sets = np.array_split(np.array(BadPost.objects.all()),CORES)
		bad_post_results = combine_bad_post_summaries(p.map(process_bad_post_set, badpost_sets))
		bad_post_results['all_posts'] = ScenarioModel.objects.all().count()
		with open('bad_post_results.txt','w+') as output_file:
			output_file.write(str(bad_post_results))


