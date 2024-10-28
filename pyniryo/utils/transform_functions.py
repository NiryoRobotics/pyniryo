import math

import numpy as np

# epsilon for testing whether a number is close to zero
_EPS = np.finfo(float).eps * 4.0

# axis sequences for Euler angles
_NEXT_AXIS = [1, 2, 0, 1]


def euler_matrix(ai, aj, ak):
    si, sj, sk = math.sin(ai), math.sin(aj), math.sin(ak)
    ci, cj, ck = math.cos(ai), math.cos(aj), math.cos(ak)
    cc, cs = ci * ck, ci * sk
    sc, ss = si * ck, si * sk

    M = np.identity(4)
    M[0, 0] = cj * ck
    M[0, 1] = sj * sc - cs
    M[0, 2] = sj * cc + ss
    M[1, 0] = cj * sk
    M[1, 1] = sj * ss + cc
    M[1, 2] = sj * cs - sc
    M[2, 0] = -sj
    M[2, 1] = cj * si
    M[2, 2] = cj * ci
    return M


def euler_from_matrix(matrix):
    M = np.array(matrix, dtype=np.float64, copy=False)[:3, :3]
    cy = math.sqrt(M[0, 0]**2 + M[1, 0]**2)
    if cy > _EPS:
        ax = math.atan2(M[2, 1], M[2, 2])
        ay = math.atan2(-M[2, 0], cy)
        az = math.atan2(M[1, 0], M[0, 0])
    else:
        ax = math.atan2(-M[1, 2], M[1, 1])
        ay = math.atan2(-M[2, 0], cy)
        az = 0.0

    return ax, ay, az


def __apply_rotation(initial_rpy, rpy_to_apply):
    initial_rotation = euler_matrix(*initial_rpy)
    rotation = euler_matrix(*rpy_to_apply)

    final_rotation = np.matmul(initial_rotation, rotation)

    final_orientation = euler_from_matrix(final_rotation)
    return final_orientation


def convert_legacy_rpy_to_dh_convention(roll, pitch, yaw):
    legacy_to_dh_rotation = (0, -np.pi / 2, np.pi)
    return __apply_rotation((roll, pitch, yaw), legacy_to_dh_rotation)


def convert_dh_convention_to_legacy_rpy(roll, pitch, yaw):
    dh_to_legacy_rotation = (np.pi, -np.pi / 2, 0)
    return __apply_rotation((roll, pitch, yaw), dh_to_legacy_rotation)
