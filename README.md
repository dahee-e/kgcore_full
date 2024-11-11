# Uncovering High-Order Cohesive Structures: Efficient (k,g)-Core Computation and Decomposition for Large Hypergraphs


##  Running (k,g)-core Algorithm

### (1) Running NPA
```
python main.py --network <network_path> --algorithm NPA --k <k_value> --g <g_value>
```



### (2) Running EPA
```
python main.py --network <network_path> --algorithm EPA --k <k_value> --g <g_value>
```

### (3) Running Decomposition
```
python main.py --network <network_path> --algorithm decom
```




#### ❗❗ Required Arguments ❗❗
```--network```: File path of the network

```--algorithm```: Specify the algorithm to use. (NPA, EPA, decom)

```--k```: The number of communities

```--g```: The number of seed nodes





##### Reference
[1] 
