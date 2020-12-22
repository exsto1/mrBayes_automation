import time


def check(filename):
    input_mcmc = open(filename).readlines()
    input_mcmc = [i for i in input_mcmc if len(i.split("\t")) > 5]
    input_mcmc = [[int(i.split("\t")[0]), float(i.split("\t")[-1].rstrip())] for i in input_mcmc[1:]]
    return input_mcmc


def threshold_check(filename, threshold_value=0.1):
    state = False
    while not state:
        temp_result = check(filename)
        print(temp_result[-1])
        if temp_result[-1][1] < threshold_value:
            state = True
            return temp_result
        else:
            time.sleep(20)
    # print("Done")


threshold_value = 0.1
filename = "test.mcmc"
