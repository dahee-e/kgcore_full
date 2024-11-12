import os
dir = "./datasets/real/"

#read all the files in the directory
file  = os.listdir(dir)
#.DS_Store and MAG file , we need to remove it
file.remove('.DS_Store')
file.remove('MAG')

file = ["instacart"]
for f in file:
    for k in range(2,10):
        for g in range (2,10):
            print(f"python main.py --network {dir}{f}/network.hyp --algorithm EPA --k {k} --g {g} &&")


#write the output to a file
with open("run.sh", "w") as f:
    for file in file:
        for k in range(2,10):
            for g in range (2,10):
                f.write(f"python main.py --network {dir}{file}/network.hyp --algorithm EPA --k {k} --g {g} &&\n")
                # f.write(f"python main.py --network {dir}{file}/network.hyp --algorithm NPA --k {k} --g {g} &&\n")
