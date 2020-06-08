# eclipse-python
Alpha beta pruning method for board game Eclipse (by Gigamic) written purely in python. 

<p float="left">
    <img src="images/scene1.png" width="250" />
    <img src="images/scene2.png" width="250" />
</p>

## Usage

``python main.py <time-sec> [white|black]``

## Additional Notes

* Computation is currently fixed to a depth of three moves rather, dynamic depth with 
Montecarlo search will be added in the future.
* Turn time exhaustion will simply break the recursion with its current max.
* Parallel tree traversing will be added.
