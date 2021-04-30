import Pathfinding.simPathMap as spm

s = spm.simPathMap([0, 0, 1], [2, 2, 1], 1, 1.0)

print(s.get_angle((18, 18), (17, 17)))

# Funktioniert
#
# (-1, 1) | (0, 1) | (1, 1)
# (-1, 0) | (0, 0) | (1, 0) | (2,0)
# (-1,-1) | (0,-1) | (1,-1)

print(s.drone_pos)
a = s.checkpoints_to_pos([(1, 1), (2, 0)], (0, 0, 1))

print(a)
