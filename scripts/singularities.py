import math
import numpy as np
import cv2

class Singularities:
    def __init__(self, image, angles, tolerance, block_size, mask):
        self.image = image
        self.angles = angles
        self.tolerance = tolerance
        self.block_size = block_size
        self.mask = mask
   
    def poincare_index_at(self, i, j, angles, tolerance):
        """
        compute the summation difference between the adjacent orientations such that the orientations is less then 90 degrees
        https://books.google.pl/books?id=1Wpx25D8qOwC&lpg=PA120&ots=9wRY0Rosb7&dq=poincare%20index%20fingerprint&hl=pl&pg=PA120#v=onepage&q=poincare%20index%20fingerprint&f=false
        :param i:
        :param j:
        :param angles:
        :param tolerance:
        :return:
        """
        cells = [(-1, -1), (-1, 0), (-1, 1),         # p1 p2 p3
                (0, 1),  (1, 1),  (1, 0),            # p8    p4
                (1, -1), (0, -1), (-1, -1)]          # p7 p6 p5

        angles_around_index = [math.degrees(angles[i - k][j - l]) for k, l in cells]
        index = 0

        for k in range(0, 8):

            # calculate the difference
            difference = angles_around_index[k] - angles_around_index[k + 1]
            if difference > 90:
                difference -= 180
            elif difference < -90:
                difference += 180

            index += difference

        if 180 - tolerance <= index and index <= 180 + tolerance:
            return "delta"
        if -180 - tolerance <= index and index <= -180 + tolerance:
            return "loop"
        if 360 - tolerance <= index and index <= 360 + tolerance:
            return "whorl"
        return "none"

    def calculate_singularities(self):
        result = cv2.cvtColor(self.image, cv2.COLOR_GRAY2RGB)

        # DELTA: RED, LOOP:ORAGNE, whorl:INK
        colors = {"loop" : (0, 0, 255), "delta" : (0, 128, 255), "whorl": (255, 153, 255)}
        loop_list = []
        loop_1d = []
        delta_list = []
        whorl_list = []

        for i in range(3, len(self.angles) - 2):   # Y
            loop = []
            delta = []
            whorl = []
            for j in range(3, len(self.angles[i]) - 2):      # x
                # mask any singularity outside of the mask
                mask_slice = self.mask[(i-2)*self.block_size:(i+3)*self.block_size, (j-2)*self.block_size:(j+3)*self.block_size]
                mask_flag = np.sum(mask_slice)
                if mask_flag == (self.block_size*5)**2:
                    singularity = self.poincare_index_at(i, j, self.angles, self.tolerance)
                else:
                    singularity = "none"

                if singularity != "none":
                    cv2.rectangle(result, ((j+0)*self.block_size, (i+0)*self.block_size), ((j+1)*self.block_size, (i+1)*self.block_size), colors[singularity], 3)
                    if singularity == "loop":
                        loop.append([(i)*self.block_size, (j)*self.block_size])
                        loop_1d.append([(i)*self.block_size, (j)*self.block_size])
                        if singularity == "delta":
                            delta.append([(i)*self.block_size, (j)*self.block_size])
                        if singularity == "whorl":
                            whorl.append([(i)*self.block_size, (j)*self.block_size])
                        #print(((j+0)*self.block_size, (i+0)*self.block_size))
                        #print(((j+1)*self.block_size, (i+1)*self.block_size))
                        #print("--------------------------")

            if len(loop) > 0:
                loop_list.append(loop)
            if len(delta) > 0:
                delta_list.append(delta)
            if len(whorl) > 0:
                whorl_list.append(whorl)

        return result, loop_1d, loop_list, delta_list, whorl_list

