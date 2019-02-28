import sys
import cPickle
import os
import json
import numpy as np
import pandas as pd
import multiprocessing as mp
from reo.models import ErrorModel, BadPost, MessageModel, ElectricTariffModel,ScenarioModel
import datetime
import pytz
import copy
import datetime
import pytz
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
			result[error[0:100]] = {'count':1,'run_uuids':[str(bp.__dict__['run_uuid'])]}
		else:
			result[error[0:100]]['count'] += 1
			result[error[0:100]]['run_uuids'].append(str(bp.__dict__['run_uuid']))
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
	
	result = {'most_recent_error':0,'count_total_errors':0,"count_new_errors":0}
	
	daily_count = {}
	
	traceback_lookup = {}
	
	now = datetime.datetime.utcnow()
	now = now.replace(tzinfo=pytz.utc)
	now = int(round((now - datetime.datetime(1970, 1, 1,tzinfo=pytz.utc)).total_seconds()))
	
	for e in e_set:
		result['count_total_errors'] +=1
		
		e_created = int(round((e.created - datetime.datetime(1970, 1, 1,tzinfo=pytz.utc)).total_seconds()))
		
		day = int(round((datetime.datetime(*e.created.timetuple()[:3],tzinfo=pytz.utc) - datetime.datetime(1970, 1, 1,tzinfo=pytz.utc)).total_seconds()))
		
		if day in daily_count.keys():
			daily_count[day] += 1
		else:
			daily_count[day] = 1

		e_traceback = e.traceback.replace(str(e.run_uuid), '<run_uuid>')
		if e_traceback not in traceback_lookup.values():
			tb_id = len(traceback_lookup.keys())
			traceback_lookup[tb_id] = e_traceback
		else:
			tb_id = [k for k,v in traceback_lookup.items() if v==e_traceback][0] 
		
		if e_created > result['most_recent_error']:
			result['most_recent_error'] = e_created

		if (e_created - now) / (60*60*24.0) < recent_interval_days:
			result['count_new_errors'] +=1

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
				if e_created > result[n][attr]['most_recent_error']:
					result[n][attr]['most_recent_error'] = e_created
			else:
				result[n][attr] = {'count_new'.format(recent_interval_days):0, 'count':1, 'most_recent_error': e_created, 'run_uuids_new':[],'run_uuids_old': []}

			if (now - e_created) / (60*60*24.0) < recent_interval_days:
				result[n][attr]['count_new_errors'] +=1
				if str(e.run_uuid) not in result[n][attr]['run_uuids_new']:
					result[n][attr]['run_uuids_new'].append(str(e.run_uuid))
			else:
				if str(e.run_uuid) not in result[n][attr]['run_uuids_old']:
					result[n][attr]['run_uuids_old'].append(str(e.run_uuid))
	
	result['traceback_lookup'] = traceback_lookup
	result['daily_count'] = daily_count
	return result 

def combine_error_summaries(error_summaries):

	result = {'traceback_lookup':{}, 'daily_count':{}}
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
			for day, count in es['daily_count'].items():
				if day not in result['daily_count'].keys():
					result['daily_count'][day] = count
				else:
					result['daily_count'][day] += count
			del es['daily_count']

	for i,es in enumerate(error_summaries):		
		if es is not None:
			for error_type in es.keys():
				if error_type not in ['traceback_lookup','daily_count']:
					if error_type not in result.keys():
						result[error_type] = copy.deepcopy(es[error_type])
					else:
						if type(es[error_type]) == int:
							if error_type not in result.keys():
								result[error_type] += es[error_type]
							else:
								if error_type.startswith('count'):
									result[error_type] += es[error_type]
								if error_type.startswith('most_recent_error'):
									if result[error_type] < es[error_type]:
										result[error_type] = es[error_type]
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
										elif attr_name == 'most_recent_error':
											if result[error_type][error_type_id][attr_name] < attr:
												result[error_type][error_type_id][attr_name] = attr
										else:	
											result[error_type][error_type_id][attr_name]+=attr
	return result


def process_urdb_set(urdb_set):

	if len(urdb_set) == 0:
		return None

	result = {"count_none":0,"count_total_uses":0,'count_total_errors':0,'count_new_errors':0,'count_new_uses':0,'most_recent_error':0,'count_urdb_plus_blended':0,'count_blended_annual':0,'count_blended_monthly':0}
	for u in urdb_set:

		urdb_label,urdb_response,run_uuid,blended_annual_demand_charges_us_dollars_per_kw,blended_annual_rates_us_dollars_per_kwh,blended_monthly_demand_charges_us_dollars_per_kw,blended_monthly_rates_us_dollars_per_kwh,add_blended_rates_to_urdb_rate = u
		
		result['count_total_uses'] += 1
		label = urdb_label or None
		if label is None:
			try:
				label = urdb_response['label']
			except:
				pass
		if label == None:
			if bool(blended_annual_demand_charges_us_dollars_per_kw) or bool(blended_annual_rates_us_dollars_per_kwh):
				result['count_blended_annual'] += 1
			if bool(blended_monthly_demand_charges_us_dollars_per_kw) or bool(blended_monthly_rates_us_dollars_per_kwh):
				result['count_blended_monthly'] += 1
			result['count_none'] += 1
		else:
			if bool(blended_monthly_demand_charges_us_dollars_per_kw) or bool(blended_monthly_rates_us_dollars_per_kwh):
				if bool(add_blended_rates_to_urdb_rate):
					result['count_urdb_plus_blended'] += 1		
			if label in result.keys():
				if str(run_uuid) not in result[label]:
					result[label].append(str(run_uuid))
			else:
				result[label] = [str(run_uuid)]

	for k,v in result.items():
		if not k.startswith('count') and k != 'most_recent_error':
			e_set = [i for i in ErrorModel.objects.filter(run_uuid__in=v)]

			result[k] = process_error_set(e_set) or {'most_recent_error':0, 'count_total_errors':0,"count_new_errors":0,'count_new_uses':0}

			result['count_total_errors']+=len(e_set) 
			result['count_new_errors']+=result[k]['count_new_errors']

			if result[k]['most_recent_error'] > result['most_recent_error']:
				result['most_recent_error']=result[k]['most_recent_error']

	return result

def combine_urdb_summaries(urdb_rates):
	print 'combining summaries', sys.getsizeof(cPickle.dumps(urdb_rates))
	
	result = {'traceback_lookup':{}}
	tb_recode = {}
	
	for u in urdb_rates:
		if u is not None:
			if 'traceback_lookup' in u.keys():
				tb_recode['traceback_lookup'] = {}
				for tb_id, tb in u['traceback_lookup'].items():
					if tb in result['traceback_lookup'].values():
						tb_recode['traceback_lookup'][tb_id] = [k for k,v in result['traceback_lookup'].items() if v==tb][0]
					else:
						if len(result['traceback_lookup'])==0:
							new_tb_id = 0
						else:
							new_tb_id = max(result['traceback_lookup'].keys())+1 
						result['traceback_lookup'][new_tb_id] = tb
						tb_recode['traceback_lookup'][tb_id] = new_tb_id				
			else:
				for rate, rate_stats in u.items():
					if rate not in tb_recode.keys():
						tb_recode[rate] = {}
					if not rate.startswith('count') and not rate.startswith('most_recent_error'):
							if 'traceback_lookup' in rate_stats.keys():
								for tb_id, tb in rate_stats['traceback_lookup'].items():
									if tb in result['traceback_lookup'].values():
										tb_recode[rate][tb_id] = [k for k,v in result['traceback_lookup'].items() if v==tb][0]
									else:
										if len(result['traceback_lookup'])==0:
											new_tb_id = 0
										else:
											new_tb_id = max(result['traceback_lookup'].keys())+1 
										result['traceback_lookup'][new_tb_id] = tb
										tb_recode[rate][tb_id] = new_tb_id
								del rate_stats['traceback_lookup']
			
	for u in urdb_rates:		
		if u is not None:
			for rate, rate_stats in u.items():
				if not rate.startswith('count') and not rate.startswith('most_recent_error'):					
					if 'traceback' in rate_stats.keys():
						if 'traceback_lookup' in u.keys():
							recode_lookup = 'traceback_lookup'
						else:
							recode_lookup = rate
						new_traceback_data = {}
						for tb_id,tb_info in rate_stats['traceback'].items():
							new_traceback_data[tb_recode[recode_lookup][tb_id]] = tb_info
						rate_stats['traceback'] = new_traceback_data
						del new_traceback_data

					if rate != 'traceback_lookup':
						if rate not in result.keys():
							result[rate] = copy.deepcopy(u[rate])
						else:
							for rate_stat_key,rate_stat_info in rate_stats.items():							
								if type(rate_stat_info)==int:
									if rate_stat_key not in result[rate].keys():
										 result[rate][rate_stat_key] = rate_stat_info
									else:
										if rate_stat_key =='most_recent_error':
											if rate_stat_info > result[rate][rate_stat_key]:
												result[rate][rate_stat_key] = rate_stat_info
										else:
											result[rate][rate_stat_key] += rate_stat_info
								else:
									if rate_stat_key not in result[rate].keys():
										result[rate][rate_stat_key] = copy.deepcopy(rate_stat_info)
									else:
										for sub_group, sub_group_data in rate_stat_info.items():
											if sub_group not in result[rate][rate_stat_key].keys():
												result[rate][rate_stat_key][sub_group] = {}
											if type(sub_group_data) == int:
												if result[rate][rate_stat_key][sub_group] == {}:
													result[rate][rate_stat_key][sub_group] = sub_group_data
												else:
													result[rate][rate_stat_key][sub_group] += sub_group_data
											else:
												for attr_name, attr in sub_group_data.items():
													if attr_name.startswith('count'):
														if attr_name in result[rate][rate_stat_key][sub_group].keys():
															result[rate][rate_stat_key][sub_group][attr_name] += attr
														else:
															result[rate][rate_stat_key][sub_group][attr_name] = attr
													elif attr_name == 'most_recent_error':
														if attr not in result[rate][rate_stat_key][sub_group].keys():
															result[rate][rate_stat_key][sub_group][attr_name] = attr
														elif result[rate][rate_stat_key][sub_group][attr_name] < attr:
															result[rate][rate_stat_key][sub_group][attr_name] = attr
													elif attr_name.startswith('run_uuid'):
														if attr_name in result[rate][rate_stat_key][sub_group].keys():
															for r_id in attr:
																if r_id not in result[rate][rate_stat_key][sub_group][attr_name]:
																	result[rate][rate_stat_key][sub_group][attr_name]+=[r_id]
														else:
															result[rate][rate_stat_key][sub_group][attr_name] = list(np.unique(attr))
													else:
														if attr_name in result[rate][rate_stat_key][sub_group].keys():
															result[rate][rate_stat_key][sub_group][attr_name]+=attr
														else:
															result[rate][rate_stat_key][sub_group][attr_name] =attr
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

		total_t = ElectricTariffModel.objects.all().count()
		urdb_results = {}
		for r in [10,11,12,13]:#range(0,int(total_t/10000.0)+1):
			start = r*10000
			end = min((r+1)*10000,total_t)
			print start, end, total_t
			tmp = np.array_split(np.array(ElectricTariffModel.objects.values_list("urdb_label","urdb_response","run_uuid","blended_annual_demand_charges_us_dollars_per_kw","blended_annual_rates_us_dollars_per_kwh","blended_monthly_demand_charges_us_dollars_per_kw","blended_monthly_rates_us_dollars_per_kwh","add_blended_rates_to_urdb_rate").all()[start:end]),CORES)
			urdb_results = combine_urdb_summaries(p.map(process_urdb_set, tmp) + [urdb_results])
		
		error_sets = np.array_split(np.array(ErrorModel.objects.all()),CORES)
		error_results = combine_error_summaries(p.map(process_error_set, error_sets))

		urdb_results,error_results, common_lookup = harmonize_traceback_lookups(urdb_results,error_results)

		summary_info ={'count_all_posts':ScenarioModel.objects.all().count(),'count_bad_posts':BadPost.objects.all().count()}

		with open('scripts/summary_info.js','w+') as output_file:
			output_file.write("var summary_info = " +  json.dumps(summary_info))

		with open('scripts/urdb_results.js','w+') as output_file:
			output_file.write("var urdb_results = " +  json.dumps(urdb_results))

		with open('scripts/error_results.js','w+') as output_file:
			output_file.write("var error_results = " + json.dumps(error_results))

		with open('scripts/common_lookup.js','w+') as output_file:
			output_file.write("var common_lookup = " +  json.dumps(common_lookup))

		badpost_sets = np.array_split(np.array(BadPost.objects.all()),CORES)
		bad_post_results = combine_bad_post_summaries(p.map(process_bad_post_set, badpost_sets))
		with open('scripts/bad_posts.js','w+') as output_file:
			output_file.write("var bad_posts = " + json.dumps(bad_post_results))