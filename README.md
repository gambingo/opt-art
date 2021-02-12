#### Considerations
1. Create the map or graph object to manage multiple ants
2. Deposit pheromoe and include that in the probabilities
3. Evaporate pheromone
4. Evaluate how well probabilities work (research this)


#### Ideas for Next Steps
[ ] Write a function to recreate selection probabilities so you don't need
to bog down iterations with pandas


#### Considerations
[ ] Should all the distances be intengers? How much does that affect the memory load or speed? Let's do some python research.
[ ] Ants should travel randomly, but should they be allowed to repeat nodes. By initial thinking is no.
[ ] To reduce the options, we could limit the number of node connections. Nodes only have valid edges within a certain radius. It doesn't make practical sense to connect a node to absolutely every single other node. (Ants would only travel within their vicinity. Let's limit how far the ant can see!)
[ ] Right now the probabilities change depending on how many valid adjacent 
nodes there are. Should we keep the probabilities consistent and just re-pick 
if a node has already been visited? I feel like I want consistent probabilities 
but don't probabistic re-picking. Hmmmm.
[ ] Could attempt to get it working with no evaporation first, and then 
incorporate evaporation to avoid local mins



#### Documenting process for presentation
1. Got everything connected, started documenting considerations
2. Ran it on 20 points and it wasn't anything special
3. Toyed with levels but saw no improvement
4. Began looking under the hood, discovered "first picks ratio"
5. New goal is to optimize that