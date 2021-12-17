import os
import sys

# Change desired dna_seq .txt file in line 125
class HidenMarkov:
    # The following specifies the hidden states
    statesSet = {'CpG', 'NotCpG'}

    """
    NOTE:  The probability numbers indicated below are in log2 form.  That is,
    the probability number =  2^number so for example 2^-1 = 0.5,  and 
    2^-2 = 0.25 ... etc.   The reason for this is that Log2 is used to represent
    probabilities so that underflow or overflow is not encounrered.  

    If you wish to change the probabilities in the tables below, than simple calculate 
    log2(probability that you want/need).  For example log2(0.33) = -0.6252,  and 
    log2(0.5) = -1,  and so forth. 
    """

    # Non-log2 values:
    # CpG 0.5 NotCpG 0.5
    
    start_probability = {"CpG": -1.0, "NotCpG": -1.0}   # Start probabilities

    # Non-log2 values:
    # CpG: 0.95 0.05
    # NotCpG: 0.1 0.9
    trans_probability = {                             # Hidden state transition probabilities
        "CpG": {"CpG": -0.152003, "NotCpG": -3.321928},
        "NotCpG": {"CpG": -4.321928, "NotCpG": -0.074001},
        }

    # Non-log2 values:
    # CpG: 0.15 0.33 0.16 0.36
    # NotCpG: 0.27 0.24 0.26 0.23
    emit_probability = {                              # Emission probabilities
        "CpG": {"A": -2.736966, "C": -1.599462, "T": -2.643856, "G": -1.473931},
        "NotCpG": {"A": -1.888969, "C": -2.058894, "T": -1.943416, "G": -2.120294},
        }

    def __init__(self, input_seq):
        self.input_seq = input_seq

    def viterbi(self, obs, states, start_p, trans_p, emit_p, file_name):
        # V is a list of dictionaries containing the hidden state probabilities of each nucleotide
        V = []
        path = {}

        states = list(states)

        # initialize V and path
        for i in range(len(obs)):
            path[i] = {}
            V.append({})

        # initialize time 0 with first observation in the dna_seq txt file
        for i in range(len(states)):
            V[0][states[i]] = start_p[states[i]] + emit_p[states[i]][obs[0]]
            path[0][states[i]] = 0

        # perform main recursion
        for t in range(1, len(obs)):
            for j in range(len(states)):
                prob, psi = max(
                    [(emit_p[states[j]][obs[t]] + trans_p[states[i]][states[j]] + V[t - 1][states[i]], i) for i in
                     range(len(states))])
                V[t][states[j]] = prob
                path[t][states[j]] = states[psi]

        # get final path probability and final state
        final_state, prob = max(V[-1].items(), key=lambda x: x[1])
        final_path = []
        final_path.insert(0, final_state)
        prev = final_state

        # perform backtrace for most probable path
        for i in range(len(path) - 1, 0, -1):
            final_path.insert(0, path[i][prev])
            prev = path[i][prev]

        cpgs = []
        i = 1
        length = len(final_path)
        total_cpgs = 0

        # recursion that iterates across the final_path list, of which the recursion records every CpG island
        # Start and End position while printing out the total amount of CpG islands found
        while i < length:
            if final_path[i] == 'CpG':
                j = i + 1
                while j < length:
                    if final_path[j] == 'NotCpG':
                        break
                    j += 1
                cpgs.append([i, j - 1])
                i = j
            i += 1
        filestring = str(file_name)
        file = "TommyNguyen_" + filestring + "_output.txt"
        # stores Start and End position of every CpG island in the text file: TommyNguyen_viterbi_output
        with open(file, "w") as f:
            f.write("Start End \n")
            print("Start End")
            for i in cpgs:
                total_cpgs += 1
                print(i[0], i[1])
                f.write(str(i[0]) + " " + str(i[1]) + "\n")
            if total_cpgs == 1:
                f.write("The program has found " + str(total_cpgs) + " CpG island")
                print()
                print("The program has found " + str(total_cpgs) + " CpG island")
            else:
                f.write("The program has found " + str(total_cpgs) + " CpG islands")
                print()
                print("The program has found " + str(total_cpgs) + " CpG islands")


        return final_path

#############

if __name__ == '__main__':
    input_seq = ""
    # Set working directory to script's directory
    file_path = os.path.abspath(sys.argv[0])
    directory = os.path.dirname(file_path)
    os.chdir(directory)
    file_input = str(input("Type in the file name, including the extension (e.g. dna_seq1.txt): "))
    does_file_exist = os.path.exists(file_input)
    if does_file_exist:
        with open(file_input) as f:  # change input to desired .txt file
            for line in f:
                stripped_line = line.rstrip().upper()
                input_seq += str(stripped_line)
            print()
            hm = HidenMarkov(input_seq)
            hm.viterbi(input_seq, hm.statesSet, hm.start_probability, hm.trans_probability, hm.emit_probability, file_input)
    else:
        print("File is not found in directory, run the program again \n")
    input_seq = ""

else:
    print("The HidenMarkov.py  module is intended to be executed and not imported.")

