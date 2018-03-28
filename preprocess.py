import argparse, sys, pickle

def findCandidates(candidate_master_filename,candidates):
	
	target_candidates = dict()
	with open(candidate_master_filename) as cn:
		for line in cn:
			info = line.split('|')
			cid = info[0]
			name = info[1]
			if name in candidates:
				target_candidates[cid] = dict()
				target_candidates[cid]["Name"] = name
				target_candidates[cid]["Party"] = info[2]
				target_candidates[cid]["State"] = info[4]
				target_candidates[cid]["Incumbent"] = (info[7] == 'I')
				target_candidates[cid]["Cmte_ID"] = set()

	return target_candidates

def linkCommittee(candidates,cc_linkfile):

	with open(cc_linkfile) as cc:
		for line in cc:
			info = line.split('|')
			cid = info[0]
			if cid in candidates:
				candidates[cid]['Cmte_ID'].add(info[3])

	return candidates

def getContributions(candidates_file,cand_cmte_linkfile,contrib_file,header_file,load_file,save_file,targets):

	if load_file != None:
		print("Loading Contributions from Pickle File....")
		with open(load_file,'rb') as cf:
			return pickle.load(cf)

	if targets == 'S':
		targets = set(["JOHNSON, RONALD HAROLD","FEINGOLD, RUSSELL DANA",\
			"TOOMEY, PATRICK JOSEPH","MCGINTY, KATHLEEN ALANA"])
	elif targets == 'P':
		targets = set(["CLINTON, HILLARY RODHAM / TIMOTHY MICHAEL KAINE",\
			"TRUMP, DONALD J. / MICHAEL R. PENCE "])

	candidates = findCandidates(candidates_file,targets)
	candidates = linkCommittee(candidates,cand_cmte_linkfile)
	added = set()
	candidate_contributions = dict()
	with open(header_file) as h:
		headers = h.read().split(',')

	with open(contrib_file) as cf:
		for j,line in enumerate(cf):
			if j%(10**6) == 0:
				print(j)
			info = line.split('|')
			cmte_id = info[0]
			sub_id = info[20]
			cid = None
			for cand_id in candidates:
				if cmte_id in candidates[cand_id]['Cmte_ID']:
					cid = cand_id

			if cid != None:
				candidate_contributions[sub_id] = dict()
				candidate_contributions[sub_id]['Candidate_ID'] = cid
				candidate_contributions[sub_id]['Candidate_Name'] = candidates[cid]['Name']
				candidate_contributions[sub_id]['Party'] = candidates[cid]['Party']
				for i,header in enumerate(headers):
					if i != 20:
						candidate_contributions[sub_id][header] = info[i]

	if save_file != None:
		print("Saving Contributions to Pickle File....")
		with open(save_file, 'wb') as cf:
			pickle.dump(candidate_contributions, cf, protocol=pickle.HIGHEST_PROTOCOL)

	return candidate_contributions

def parse_arguments():
	parser = argparse.ArgumentParser(description='Election Data Preprocess Parser')
	parser.add_argument('--candidates',dest='candidate_file',type=str,help = 'Candidates Master File Path')
	parser.add_argument('--cmte_link',dest='cand_cmte_linkfile',type=str,help='File linking candidate ID to committee ids')
	parser.add_argument('--contrib',dest='contrib_file',type=str,help='File containing individual contributions made to committees')
	parser.add_argument('--header',dest='header_file',type=str,help='CSV header file for contributions file')
	parser.add_argument('--targets',dest='targets',type=str,help='S or P for senate or presidential candidates',default='S')
	parser.add_argument('--save_file',dest='save_file',type=str,default=None,help='Optional Pickle File to save dictionary')
	parser.add_argument('--load_file',dest='load_file',type=str,default = None,help = 'Optional Pickle File to load dictionary')
	
	return parser.parse_args()

def main(args):

	args = parse_arguments()
	contributions = getContributions(args.candidate_file,args.cand_cmte_linkfile,\
		args.contrib_file,args.header_file,args.load_file,args.save_file,args.targets)
	print(len(contributions))

if __name__ == "__main__":
	main(sys.argv)

