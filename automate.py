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


def full_process_wraper(index_number, nexus_file, mcmc_file, threshold):
    def threshold_check(mcmc_filename, threshold_value=0.1):  # Wait a minute, then check every 20 seconds
        def load_data(mcmc_filename_to_load):  # Open and read content of the file
            input_mcmc = open(mcmc_filename_to_load).readlines()
            input_mcmc = [i for i in input_mcmc if len(i.split("\t")) > 5]
            input_mcmc = [[int(i.split("\t")[0]), float(i.split("\t")[-1].rstrip())] for i in input_mcmc[1:]]
            return input_mcmc

        time.sleep(60)
        state = False
        while not state:
            temp_result = load_data(mcmc_filename)
            print(temp_result[-1])
            if temp_result[-1][1] < threshold_value:
                state = True
                print("Done! Tree " + str(index_number))
                return temp_result

            else:
                time.sleep(20)

    full_command = ["mb", nexus_file]
    tree_process = subprocess.Popen(full_command)

    threshold_check(mcmc_file, threshold)

    tree_process.kill()


def main():
    nexus_file_no_params = "TEST.nexus"
    nexus_file_with_params = "NEWNAME.nexus"
    mcmc_filename = nexus_file_with_params.rstrip(".nexus") + ".mcmc"
    standard_deviation_threshold_value = 0.1

    # input_file_prepare(nexus_file_no_params, nexus_file_with_params)
    params_list = [[i, nexus_file_with_params, mcmc_filename, standard_deviation_threshold_value] for i in range(3)]
    print(params_list)
    with mp.Pool(3) as p:
        p.starmap(full_process_wraper, params_list)


if __name__ == "__main__":
    main()


# TODO
"""
0. Prepare nexus input file --- OK
1. Start multiprocessing Pool (3 trees) --- X
    1.1. Start process with known ID. --- OK
    1.2. Trace progress of the tree building. --- OK
    1.3. Check when quality will drop below threshold. --- OK
    1.4. Terminate process. --- OK
    1.5. Save parameters and generation to the file. --- X
2. Wait for all processes to finish. --- X
3. Compare results to other values of the parameter. --- X
4. Find local minimum - hoping it's global minimum as well. (Subject to change) --- X


NOTES:
- Check 1 parameter with others freezed.
- Pick best value
- Move to the next param.
- ...  
"""
