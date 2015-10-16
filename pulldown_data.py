import brigalaxy as bg
import sys, os

def main(argv):

    # Initialize Session manager object
    print "Connecting to Galaxy..."
    sm = bg.SessionManager(user_num=0, target_dir="outDir")

    # Initialize History manager object
    print "Initializing History manager..."
    hm = bg.HistoryManager(sm.gi, history_id='bd9802014d926144')


    # Get dataset graph for history
    print "Building Dataset graph..."
    dataset_graph = hm.show_dataset_graph()

    # Get list of input datasets
    print "Identifying input Datasets..."
    input_dataset_list = hm.show_input_datasets()

    print "Getting ouptut data..."
    for i in input_dataset_list[0:1]:

        rc = bg.ResultCollector(hm, dataset_graph, i)
        print "\nCollecting outputs for library:", rc.lib
        output_dataset_list = rc.show_output_list()

        print "Downloading files..."
        for o in output_dataset_list:
    #         print ResultDownloader(sm, rc.lib, o).show()
            rd = bg.ResultDownloader(sm, rc.lib, o)
            print " > Dataset:", rd.dname
            print " -- ", rd.go()
    print "\nDone."

if __name__ == "__main__":
   main(sys.argv[1:])
