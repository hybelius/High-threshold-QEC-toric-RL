import numpy as np
import matplotlib.pyplot as plt
from random import uniform, randint
from collections import namedtuple
from .util import Action, Perspective


class Toric_code():
    def __init__(self, size):
        self.system_size = size
        self.plaquette_matrix = np.zeros((self.system_size, self.system_size), dtype=int)   # dont use self.plaquette
        self.vertex_matrix = np.zeros((self.system_size, self.system_size), dtype=int)      # dont use self.vertex 
        self.qubit_matrix = np.zeros((2, self.system_size, self.system_size), dtype=int)
        self.current_state = np.stack((self.vertex_matrix, self.plaquette_matrix,), axis=0)
        self.next_state = np.stack((self.vertex_matrix, self.plaquette_matrix), axis=0)
        self.ground_state = True    # True: only trivial loops, 
                                    # False: non trivial loop 
        self.rule_table = np.array(([[0,1,2,3],[1,0,3,2],[2,3,0,1],[3,2,1,0]]), dtype=int)  # Identity = 0
                                                                                            # pauli_x = 1
                                                                                            # pauli_y = 2
                                                                                            # pauli_z = 3


    def generate_random_error(self, p_error):
        for i in range(2):
            qubits = np.random.uniform(0, 1, size=(self.system_size, self.system_size))
            error = qubits > p_error
            no_error = qubits < p_error
            qubits[error] = 0
            qubits[no_error] = 1
            pauli_error = np.random.randint(3, size=(self.system_size, self.system_size)) + 1
            self.qubit_matrix[i,:,:] = np.multiply(qubits, pauli_error)
        self.syndrom('state')

        
    def generate_n_random_errors(self, n):
        errors = np.random.randint(3, size = n) + 1
        qubit_matrix_error = np.zeros(2*self.system_size**2)
        qubit_matrix_error[:n] = errors
        np.random.shuffle(qubit_matrix_error)
        self.qubit_matrix[:,:,:] = qubit_matrix_error.reshape(2, self.system_size, self.system_size)
        self.syndrom('state')


    def step(self, action):
        # uses as input np.array of form (qubit_matrix=int, row=int, col=int, add_operator=int)
        qubit_matrix = action.position[0]
        row = action.position[1]
        col = action.position[2]
        add_operator = action.action

        old_operator = self.qubit_matrix[qubit_matrix, row, col]
        new_operator = self.rule_table[int(old_operator), int(add_operator)]
        self.qubit_matrix[qubit_matrix, row, col] = new_operator        
        self.syndrom('next_state')
    


    def syndrom(self, state):
        # generate vertex excitations (charge)
        # can be generated by z and y errors 
        qubit0 = self.qubit_matrix[0,:,:]        
        y_errors = (qubit0 == 2).astype(int) # separate y and z errors from x 
        z_errors = (qubit0 == 3).astype(int)
        charge = y_errors + z_errors # vertex_excitation
        charge_shift = np.roll(charge, 1, axis=0) 
        charge = charge + charge_shift
        charge0 = (charge == 1).astype(int) # annihilate two syndroms at the same place in the grid
        
        qubit1 = self.qubit_matrix[1,:,:]        
        y_errors = (qubit1 == 2).astype(int)
        z_errors = (qubit1 == 3).astype(int)
        charge = y_errors + z_errors
        charge_shift = np.roll(charge, 1, axis=1)
        charge1 = charge + charge_shift
        charge1 = (charge1 == 1).astype(int)
        
        charge = charge0 + charge1
        vertex_matrix = (charge == 1).astype(int)
        
        # generate plaquette excitation (flux)
        # can be generated by x and y errors
        qubit0 = self.qubit_matrix[0,:,:]        
        x_errors = (qubit0 == 1).astype(int)
        y_errors = (qubit0 == 2).astype(int)
        flux = x_errors + y_errors # plaquette_excitation
        flux_shift = np.roll(flux, -1, axis=1)
        flux = flux + flux_shift
        flux0 = (flux == 1).astype(int)
        
        qubit1 = self.qubit_matrix[1,:,:]        
        x_errors = (qubit1 == 1).astype(int)
        y_errors = (qubit1 == 2).astype(int)
        flux = x_errors + y_errors
        flux_shift = np.roll(flux, -1, axis=0)
        flux1 = flux + flux_shift
        flux1 = (flux1 == 1).astype(int)

        flux = flux0 + flux1
        plaquette_matrix = (flux == 1).astype(int)

        if state == 'state':
            self.current_state = np.stack((vertex_matrix, plaquette_matrix), axis=0)
        elif state == 'next_state':
            self.next_state = np.stack((vertex_matrix, plaquette_matrix), axis=0)

    
    def terminal_state(self, state):    # 0: terminal state
                                        # 1: not terminal state
        terminal = np.all(state==0)
        if terminal == True:
            return 0
        else:
            return 1


    def eval_ground_state(self):    # True: trivial loop
                                    # False: non trivial loop
	       # can only distinguish non trivial and trivial loop. Categorization what kind of non trivial loop does not work 
            # function works only for odd grid dimensions! 3x3, 5x5, 7x7        
        def split_qubit_matrix_in_x_and_z():
        # loops vertex space qubit matrix 0
            z_matrix_0 = self.qubit_matrix[0,:,:]        
            y_errors = (z_matrix_0 == 2).astype(int)
            z_errors = (z_matrix_0 == 3).astype(int)
            z_matrix_0 = y_errors + z_errors 
            # loops vertex space qubit matrix 1
            z_matrix_1 = self.qubit_matrix[1,:,:]        
            y_errors = (z_matrix_1 == 2).astype(int)
            z_errors = (z_matrix_1 == 3).astype(int)
            z_matrix_1 = y_errors + z_errors
            # loops plaquette space qubit matrix 0
            x_matrix_0 = self.qubit_matrix[0,:,:]        
            x_errors = (x_matrix_0 == 1).astype(int)
            y_errors = (x_matrix_0 == 2).astype(int)
            x_matrix_0 = x_errors + y_errors 
            # loops plaquette space qubit matrix 1
            x_matrix_1 = self.qubit_matrix[1,:,:]        
            x_errors = (x_matrix_1 == 1).astype(int)
            y_errors = (x_matrix_1 == 2).astype(int)
            x_matrix_1 = x_errors + y_errors

            return x_matrix_0, x_matrix_1, z_matrix_0, z_matrix_1

        x_matrix_0, x_matrix_1, z_matrix_0, z_matrix_1 = split_qubit_matrix_in_x_and_z()
        
        loops_0 = np.sum(np.sum(x_matrix_0, axis=0))
        loops_1 = np.sum(np.sum(x_matrix_1, axis=0))
        
        loops_2 = np.sum(np.sum(z_matrix_0, axis=0))
        loops_3 = np.sum(np.sum(z_matrix_1, axis=0))

        if loops_0%2 == 1 or loops_1%2 == 1:
            self.ground_state = False
        elif loops_2%2 == 1 or loops_3%2 == 1:
            self.ground_state = False


    def rotate_state(self, state):
        vertex_matrix = state[0,:,:]
        plaquette_matrix = state[1,:,:]
        rot_plaquette_matrix = np.rot90(plaquette_matrix)
        rot_vertex_matrix = np.rot90(vertex_matrix)
        rot_vertex_matrix = np.roll(rot_vertex_matrix, 1, axis=0)
        rot_state = np.stack((rot_vertex_matrix, rot_plaquette_matrix), axis=0)
        return rot_state


    def generate_perspective(self, grid_shift, state):
        def mod(index, shift):
            index = (index + shift) % self.system_size 
            return index
        perspectives = []
        vertex_matrix = state[0,:,:]
        plaquette_matrix = state[1,:,:]
        # qubit matrix 0
        for i in range(self.system_size):
            for j in range(self.system_size):
                if vertex_matrix[i, j] == 1 or vertex_matrix[mod(i, 1), j] == 1 or \
                plaquette_matrix[i, j] == 1 or plaquette_matrix[i, mod(j, -1)] == 1:
                    new_state = np.roll(state, grid_shift-i, axis=1)
                    new_state = np.roll(new_state, grid_shift-j, axis=2)
                    temp = Perspective(new_state, (0,i,j))
                    perspectives.append(temp)
        # qubit matrix 1
        for i in range(self.system_size):
            for j in range(self.system_size):
                if vertex_matrix[i,j] == 1 or vertex_matrix[i, mod(j, 1)] == 1 or \
                plaquette_matrix[i,j] == 1 or plaquette_matrix[mod(i, -1), j] == 1:
                    new_state = np.roll(state, grid_shift-i, axis=1)
                    new_state = np.roll(new_state, grid_shift-j, axis=2)
                    new_state = self.rotate_state(new_state) # rotate perspective clock wise
                    temp = Perspective(new_state, (1,i,j))
                    perspectives.append(temp)
        
        return perspectives


    def generate_memory_entry(self, action, reward, grid_shift):
        def shift_state(row, col):
            perspective = np.roll(self.current_state, grid_shift-row, axis=1)
            perspective = np.roll(perspective, grid_shift-col, axis=2)
            next_perspective = np.roll(self.next_state, grid_shift-row, axis=1)
            next_perspective = np.roll(next_perspective, grid_shift-col, axis=2)
            return perspective, next_perspective
        qubit_matrix = action.position[0]
        row = action.position[1]
        col = action.position[2]
        add_operator = action.action
        if qubit_matrix == 0:
            perspective, next_perspective = shift_state(row, col)
            action = Action((0, grid_shift, grid_shift), add_operator)
        elif qubit_matrix == 1:
            perspective, next_perspective = shift_state(row, col)
            perspective = self.rotate_state(perspective)
            next_perspective = self.rotate_state(next_perspective)
            action = Action((1, grid_shift, grid_shift), add_operator)
        terminal = self.terminal_state(next_perspective)
        return perspective, action, reward, next_perspective, terminal 


    def plot_toric_code(self, state, title):
        x_error_qubits1 = np.where(self.qubit_matrix[0,:,:] == 1)
        y_error_qubits1 = np.where(self.qubit_matrix[0,:,:] == 2)
        z_error_qubits1 = np.where(self.qubit_matrix[0,:,:] == 3)

        x_error_qubits2 = np.where(self.qubit_matrix[1,:,:] == 1)
        y_error_qubits2 = np.where(self.qubit_matrix[1,:,:] == 2)
        z_error_qubits2 = np.where(self.qubit_matrix[1,:,:] == 3)

        vertex_matrix = state[0,:,:]
        plaquette_matrix = state[1,:,:]
        vertex_defect_coordinates = np.where(vertex_matrix)
        plaquette_defect_coordinates = np.where(plaquette_matrix)

        #xLine = np.linspace(0, self.system_size-0.5, self.system_size)
        xLine = np.linspace(0, self.system_size, self.system_size)
        x = range(self.system_size)
        X, Y = np.meshgrid(x,x)
        XLine, YLine = np.meshgrid(x, xLine)

        markersize_qubit = 15
        markersize_excitation = 7
        markersize_symbols = 7
        linewidth = 2

        ax = plt.subplot(111)
        ax.plot(XLine, -YLine, 'black', linewidth=linewidth)
        ax.plot(YLine, -XLine, 'black', linewidth=linewidth)
        
        # add the last two black lines 
        ax.plot(XLine[:,-1] + 1.0, -YLine[:,-1], 'black', linewidth=linewidth)
        ax.plot(YLine[:,-1], -YLine[-1,:], 'black', linewidth=linewidth)

        ax.plot(X + 0.5, -Y, 'o', color = 'black', markerfacecolor = 'white', markersize=markersize_qubit+1)
        ax.plot(X, -Y -0.5, 'o', color = 'black', markerfacecolor = 'white', markersize=markersize_qubit+1)
        # add grey qubits
        ax.plot(X[-1,:] + 0.5, -Y[-1,:] - 1.0, 'o', color = 'black', markerfacecolor = 'grey', markersize=markersize_qubit+1)
        ax.plot(X[:,-1] + 1.0, -Y[:,-1] - 0.5, 'o', color = 'black', markerfacecolor = 'grey', markersize=markersize_qubit+1)
        
        # all x errors 
        ax.plot(x_error_qubits1[1], -x_error_qubits1[0] - 0.5, 'o', color = 'r', label="x error", markersize=markersize_qubit)
        ax.plot(x_error_qubits2[1] + 0.5, -x_error_qubits2[0], 'o', color = 'r', markersize=markersize_qubit)
        ax.plot(x_error_qubits1[1], -x_error_qubits1[0] - 0.5, 'o', color = 'black', markersize=markersize_symbols, marker=r'$X$')    
        ax.plot(x_error_qubits2[1] + 0.5, -x_error_qubits2[0], 'o', color = 'black', markersize=markersize_symbols, marker=r'$X$')

        # all y errors
        ax.plot(y_error_qubits1[1], -y_error_qubits1[0] - 0.5, 'o', color = 'blueviolet', label="y error", markersize=markersize_qubit)
        ax.plot(y_error_qubits2[1] + 0.5, -y_error_qubits2[0], 'o', color = 'blueviolet', markersize=markersize_qubit)
        ax.plot(y_error_qubits1[1], -y_error_qubits1[0] - 0.5, 'o', color = 'black', markersize=markersize_symbols, marker=r'$Y$')
        ax.plot(y_error_qubits2[1] + 0.5, -y_error_qubits2[0], 'o', color = 'black', markersize=markersize_symbols, marker=r'$Y$')

        # all z errors 
        ax.plot(z_error_qubits1[1], -z_error_qubits1[0] - 0.5, 'o', color = 'b', label="z error", markersize=markersize_qubit)
        ax.plot(z_error_qubits2[1] + 0.5, -z_error_qubits2[0], 'o', color = 'b', markersize=markersize_qubit)
        ax.plot(z_error_qubits1[1], -z_error_qubits1[0] - 0.5, 'o', color = 'black', markersize=markersize_symbols, marker=r'$Z$')
        ax.plot(z_error_qubits2[1] + 0.5, -z_error_qubits2[0], 'o', color = 'black', markersize=markersize_symbols  , marker=r'$Z$')


        #ax.plot(vertex_defect_coordinates[1], -vertex_defect_coordinates[0], 'x', color = 'blue', label="charge", markersize=markersize_excitation)
        ax.plot(vertex_defect_coordinates[1], -vertex_defect_coordinates[0], 'o', color = 'blue', label="charge", markersize=markersize_excitation)
        ax.plot(plaquette_defect_coordinates[1] + 0.5, -plaquette_defect_coordinates[0] - 0.5, 'o', color = 'red', label="flux", markersize=markersize_excitation)
        ax.axis('off')
        
        #plt.title(title)
        plt.axis('equal')
        plt.savefig('plots/graph_'+str(title)+'.png')
        plt.close()
        
