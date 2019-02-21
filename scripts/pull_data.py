import os
import numpy as np
import pandas as pd
import multiprocessing as mp
from reo.models import ErrorModel, BadPost, MessageModel
import datetime
import pytz
import copy

recent_interval_days = 7


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
				result[k] += v

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
			e_traceback = tb_id
		else:
			e_traceback = [k for k,v in traceback_lookup.items() if v==e_traceback][0] 
		
		for n in ['task','name','message', 'traceback']:
			
			if n not in result.keys():
				result[n] = {}
			
			if n == 'message':
				 e.message = e.message.replace(e.run_uuid,'<run_uuid>')

			attr =  getattr(e,n)
			if n == 'traceback':
				attr = e_traceback

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
	for es in error_summaries:
		if es is not None:
			tb_recode = {}
			for tb_id, tb in es['traceback_lookup'].items():
				if tb in result['traceback_lookup'].values():
					tb_recode[tb_id] = [k for k,v in result['traceback_lookup'].items() if v==tb][0]
				else:
					new_tb_id = len(result['traceback_lookup']) 
					result['traceback_lookup'][new_tb_id] = tb
					tb_recode[tb_id] = new_tb_id
			
	for es in error_summaries:		
		if es is not None:
			for k in es.keys():
				if k != 'traceback_lookup':
					if k not in result.keys():
						result[k] = copy.deepcopy(es[k])
					else:
						for v in es[k].keys():
							if k == 'traceback':
								v = tb_recode[v]
							
							if v not in result[k].keys():
								result[k][v] = copy.deepcopy(es[k][v])
							else:
								for attr_name, attr in es[k][v].items():
									if attr_name.startswith('count'):
										if v in result[k].keys():
											result[k][v][attr_name] += attr
										else:
											result[k][v][attr_name] = attr
									elif attr_name == 'most_recent':
										if result[k][v][attr_name] < attr:
											result[k][v][attr_name] = attr
									else:	
										result[k][v][attr_name]+=attr
	return result

def run(*args):
	CORES = 1
	
	if 'pull_data' not in globals().values():
		p = mp.Pool(processes=CORES)	
		

		
		error_sets = np.array_split(np.array(ErrorModel.objects.all()),CORES)
		error_results = combine_error_summaries(p.map(process_error_set, error_sets))

		badpost_sets = np.array_split(np.array(BadPost.objects.all()),CORES)
		bad_post_results = combine_bad_post_summaries(p.map(process_bad_post_set, badpost_sets))
		
		with open('error_results.txt','w+') as output_file:
			output_file.write(str(error_results))

		with open('bad_post_results.txt','w+') as output_file:
			output_file.write(str(bad_post_results))
