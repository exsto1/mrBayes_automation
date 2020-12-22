import time
import subprocess
import multiprocessing as mp


def input_file_prepare(input_filename, newname):  # Append mrBayes part into .nexus file with desired parameters
    append_text = "\n".join(
        [r"begin mrbayes;", "set autoclose=yes nowarnings=yes;", f"execute {newname};", "prset aamodelpr=fixed(Vt);",
         "mcmc ngen=200000 samplefreq=5000;", "end;"])
    temp_file = open(input_filename).read()
    newfile = open(newname, "w")
    newfile.write(temp_file)
    newfile.write(append_text)


def save_results_to_file(filename, starmap_output, checkpoints):
    log = open(filename, "a+")
    pos = 0
    temp = []
    for i in range(len(starmap_output)):
        for i1 in range(len(starmap_output[i])):
            if starmap_output[i][i1][1] < checkpoints[pos]:
                pos += 1
                temp.append(starmap_output[i][i1][0])

        log.write(";".join(temp) + "\n")
    log.close()


def full_process_wraper(index_number, nexus_file, mcmc_file, threshold):
    def threshold_check(mcmc_filename, threshold_value=0.1):  # Wait 40 sec, then check every 10 seconds
        def load_data(mcmc_filename_to_load):  # Open and read content of the file
            input_mcmc = open(mcmc_filename_to_load).readlines()
            input_mcmc = [i for i in input_mcmc if len(i.split("\t")) > 5]
            input_mcmc = [[int(i.split("\t")[0]), float(i.split("\t")[-1].rstrip())] for i in input_mcmc[1:]]
            return input_mcmc

        time.sleep(40)
        state = False
        while not state:
            temp_result = load_data(mcmc_filename)
            print(temp_result[-1])
            if temp_result[-1][1] < threshold_value:
                state = True
                print("Done! Tree " + str(index_number))
                return temp_result

            else:
                time.sleep(10)

    full_command = ["mb", nexus_file]
    tree_process = subprocess.Popen(full_command)

    result = threshold_check(mcmc_file, threshold)

    tree_process.kill()

    return result


def main():
    name_of_the_analysis = round(time.time(), 1)
    log_file = "log.txt"
    standard_deviation_threshold_value = 0.07
    number_of_parallel_trees = 3
    checkpoints = [0.1, 0.09, 0.08, 0.07]
    with open("log.txt", "a") as temp:
        temp.write("Analysis: " + str(name_of_the_analysis) + "\n")
        temp.write("C: " + ";".join([str(i) for i in checkpoints]) + "\n")

    nexus_file_no_params = "TEST.nexus"
    nexus_file_with_params = "NEWNAME.nexus"
    mcmc_filename = nexus_file_with_params.rstrip(".nexus") + ".mcmc"

    # input_file_prepare(nexus_file_no_params, nexus_file_with_params)
    params_list = [[i, nexus_file_with_params, mcmc_filename, standard_deviation_threshold_value] for i in range(number_of_parallel_trees)]
    with mp.Pool(min([number_of_parallel_trees, mp.cpu_count()])) as p:
        result = p.starmap(full_process_wraper, params_list)

    save_results_to_file(log_file)


if __name__ == "__main__":
    main()


# TODO
"""
0. Prepare nexus input file --- OK
    0.0. Copy base of the Nexus alignment. --- OK
    0.1. Add fixed parts with mrBayes tags start, end, run tree --- OK
    0.2. Add parts with changed parameters - prset, chains etc... --- OK?
    0.3. Save file with new name --- OK
1. Start multiprocessing Pool (3 trees) --- OK
    1.0. Start Multiprocessing Pool --- OK
    1.1. Map all the parameters to iterables and run starmap function --- OK
    1.1. Start process with known PIDs. --- OK
    1.2. Trace progress of the tree building. --- OK
    1.3. Check when quality will drop below threshold. --- OK
    1.4. Terminate process. --- OK
    1.5. Save parameters and generation to the file. --- OK?
2. Wait for all processes to finish. --- OK?
3. Compare results to other values of the parameter. --- X
4. Pick best value and freeze it. --- X
5. Continue the process untill every parameter will be optimized. --- X  
"""

