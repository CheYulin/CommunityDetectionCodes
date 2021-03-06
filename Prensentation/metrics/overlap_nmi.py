import math
import numpy as np


def calc_overlap_nmi(num_vertices, result_comm_list, ground_truth_comm_list):
    return OverlapNMI(num_vertices, result_comm_list, ground_truth_comm_list).calculate_overlap_nmi()


class OverlapNMI:
    @staticmethod
    def entropy(num):
        return -num * math.log(2, num)

    def __init__(self, num_vertices, result_comm_list, ground_truth_comm_list):
        self.x_comm_list = result_comm_list
        self.y_comm_list = ground_truth_comm_list
        self.num_vertices = num_vertices

    def calculate_overlap_nmi(self):
        def get_cap_x_given_cap_y(cap_x, cap_y):
            def get_joint_distribution(comm_x, comm_y):
                prob_matrix = np.ndarray(shape=(2, 2), dtype=float)
                intersect_size = float(len(set(comm_x) & set(comm_y)))
                cap_n = self.num_vertices + 4
                # first dim : comm_x, second dim: comm_y
                prob_matrix[1][1] = (intersect_size + 1) / cap_n
                prob_matrix[1][0] = (len(comm_x) - intersect_size + 1) / cap_n
                prob_matrix[0][1] = (len(comm_y) - intersect_size + 1) / cap_n
                prob_matrix[0][0] = (self.num_vertices - intersect_size + 1) / cap_n
                return prob_matrix

            def get_single_distribution(comm):
                prob_arr = [0] * 2
                prob_arr[1] = float(len(comm)) / self.num_vertices
                prob_arr[0] = 1 - prob_arr[1]
                return prob_arr

            def get_cond_entropy(comm_x, comm_y):
                prob_matrix = get_joint_distribution(comm_x, comm_y)
                entropy_list = map(OverlapNMI.entropy,
                                   (prob_matrix[0][0], prob_matrix[0][1], prob_matrix[1][0], prob_matrix[1][1]))
                # only consider eligible condition random variables(comm_y)
                # these far from being the negatives of comm_x
                if entropy_list[3] + entropy_list[0] <= entropy_list[1] + entropy_list[2]:
                    return np.inf
                else:
                    prob_arr_y = get_single_distribution(comm_y)
                    return sum(entropy_list) - sum(map(OverlapNMI.entropy, prob_arr_y))

            partial_res_list = []
            for comm_x in cap_x:
                cond_entropy_list = map(lambda comm_y: get_cond_entropy(comm_x, comm_y), cap_y)
                min_cond_entropy = float(min(cond_entropy_list))
                partial_res_list.append(
                    min_cond_entropy / sum(map(OverlapNMI.entropy, get_single_distribution(comm_x))))
            return np.mean(partial_res_list)

        # close to one iff cap_x =f(cap_y), there is a mapping from the ground truth to the computed result
        return 1 - 0.5 * get_cap_x_given_cap_y(self.x_comm_list, self.y_comm_list) - 0.5 * get_cap_x_given_cap_y(
            self.y_comm_list, self.x_comm_list)


if __name__ == '__main__':
    print calc_overlap_nmi(9, [[0, 1, 5], [1, 2, 3, 4, 7, 8]], [[0, 1, 2, 3, 4, 5, 7, 8], [0, 5]])
