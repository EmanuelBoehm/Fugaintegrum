import Pathfinding.simPathMap as PathMap
import Pathfinding.aStar as AStar

simPathMap = PathMap.simPathMap([0, 0, 0], [5, 20, 0], radius=5, pixel_size=0.5)

simPathMap.path_map[30][10:30] = 1

simPathMap.path_map[45][0:25] = 1

simPathMap.plot_map()

path = AStar.calc_path(simPathMap)

# Correct
checkpoints = AStar.create_checkpoints(path)
print(checkpoints)

pos_points = simPathMap.checkpoints_to_pos(checkpoints, [0, 0, 0])
print(pos_points)

simPathMap.visualize_path(path)
