import preprocess
import sys, argparse, pickle, numpy as np, matplotlib.pyplot as plt

def contributions_by_state(args,save_file = None,load_file=None):

	if load_file != None:
		print("Loading State-Wise Contributions from Pickle File....")
		with open(load_file,'rb') as cf:
			return pickle.load(cf)

	contributions = preprocess.getContributions(args.candidate_file,args.cand_cmte_linkfile\
		,args.contrib_file,args.header_file,args.contrib_load_file,None,args.targets)

	print("Categorizing by State...")

	state_party_contrib = dict()
	total_donations = dict()
	for sub_id in contributions:
		party = contributions[sub_id]['Party']
		transaction_amt = float(contributions[sub_id]['TRANSACTION_AMT'])
		state = contributions[sub_id]['STATE']

		if state == "":
			continue

		if state not in state_party_contrib:
			state_party_contrib[state] = dict()

		if party not in state_party_contrib[state]:
			state_party_contrib[state][party] = 0.0

		state_party_contrib[state][party] += transaction_amt


	if save_file != None:
		print("Saving State-Wise Contributions to Pickle File....")
		with open(save_file, 'wb') as cf:
			pickle.dump(state_party_contrib, cf, protocol=pickle.HIGHEST_PROTOCOL)

	return state_party_contrib

def analyze_states(args,states=None,load_file=None,save_file=None):

	state_party_contrib = contributions_by_state(args,\
			load_file=load_file,save_file=save_file)

	if states == None:
		states = list(state_party_contrib.keys())

	# republican = np.array([state_party_contrib[state]['REP'] if 'REP' in state_party_contrib[state] else 0.0 for state in states])
	# democrat = np.array([state_party_contrib[state]['DEM'] if 'DEM' in state_party_contrib[state] else 0.0 for state in states])


	# rep_mean = np.mean(republican)
	# dem_mean = np.mean(democrat)
	# republican = republican/rep_mean
	# democrat = democrat/dem_mean

	total = dict()
	total['REP'] = 0.0
	total['DEM'] = 0.0
	for state in state_party_contrib:
		for party in state_party_contrib[state]:
			if party == 'REP':
				total['REP'] += state_party_contrib[state][party]
			elif party == 'DEM':
				total['DEM'] += state_party_contrib[state][party]

	differences = []
	for state in state_party_contrib:
		if 'DEM' not in state_party_contrib[state] and 'REP' in state_party_contrib[state]:
			differences.append((state,-state_party_contrib[state]['REP']/total['REP']))

		elif 'REP' not in state_party_contrib[state] and 'DEM' in state_party_contrib[state]:
			differences.append((state,state_party_contrib[state]['DEM']/total['DEM']))

		else:
			differences.append((state,state_party_contrib[state]['DEM']/total['DEM']\
				-state_party_contrib[state]['REP']/total['REP']))

	differences = list(reversed(sorted(differences,key = lambda x: x[1])))
	diff = [d[1] for d in differences[0:5]]
	rep_differences = list(reversed([d[1] for d in differences[-1:-6:-1]]))
	diff.extend(rep_differences)
	st = [s[0] for s in differences[0:5]]
	rep_states = list(reversed([s[0] for s in differences[-1:-6:-1]]))
	st.extend(rep_states)

	index = np.arange(len(diff))
	bar_width = 0.5
	opacity = 0.8

	fig, ax = plt.subplots()

	diff = np.array(diff)
	dem_mask = diff >= 0.0
	rep_mask = diff < 0.0

	rep = plt.bar(index[rep_mask], diff[rep_mask], bar_width,
				 alpha=opacity,
				 color='r',
				 label='Higher than average for GOP')

	dem = plt.bar(index[dem_mask], diff[dem_mask], bar_width,
				 alpha=opacity,
				 color='b',
				 label='Higher than average for DNC')


	plt.xlabel('Region')
	plt.ylabel('Differences between mean deviations')
	plt.title('Relative impact of state on party')
	plt.xticks(index, st)
	plt.legend()

	plt.tight_layout()
	plt.show()

def parse_arguments():
	parser = argparse.ArgumentParser(description='Election Data Preprocess Parser')
	parser.add_argument('--candidates',dest='candidate_file',default=None,type=str,\
		help = 'Candidates Master File Path. Needed if contrib_load_file not provided.')
	parser.add_argument('--cmte_link',dest='cand_cmte_linkfile',default=None,type=str,\
		help='File linking candidate ID to committee ids. Needed if contrib_load_file not provided.')
	parser.add_argument('--contrib',dest='contrib_file',type=str,default=None,\
		help='File containing individual contributions made to committees. Needed if contrib_load_file not provided.')
	parser.add_argument('--header',dest='header_file',type=str,default=None,\
		help='CSV header file for contributions file. Needed if contrib_load_file not provided.')
	parser.add_argument('--targets',dest='targets',type=str,help='S or P for senate or presidential candidates',default='S')
	parser.add_argument('--contrib_load_file',dest='contrib_load_file',type=str,default = None,help = 'Optional Pickle File to load dictionary')
	return parser.parse_args()

def main(args):

	args = parse_arguments()

	if args.contrib_load_file == None and (args.candidate_file == None or args.cand_cmte_linkfile == None\
	 or args.contrib_file == None or args.header_file == None):
		print("ERROR: Either contribution load file or files to generate it need to be provided. Check help.")
		return

	states = ['OH']
	analyze_states(args,load_file="data/state_party_contrib_presidential_all.pickle",states=states)

if __name__ == "__main__":
	main(sys.argv)