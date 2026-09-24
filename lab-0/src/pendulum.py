# import sine function
from math import sin
# import plotting utilities
import matplotlib.pyplot as plt

def simulate_pendulum(x_0, L, N, dt):
    T = [0.] # first time step
    X_1 = [x_0[0]]
    X_2 = [x_0[1]]

    for k in range(N-1):
        X_1.append( X_1[k] + dt * X_2[k] )
        x_2_dot = -9.81/L*sin(X_1[k])
        X_2.append( X_2[k] + dt * x_2_dot )
        T.append( T[k] + dt )

    return T, X_1, X_2

def simulate_pendulum_with_friction(x_0, L, q, N, dt):
    # TODO: Complete this method
    
    return

def simulate_pendulum_odeint():
    from scipy.integrate import odeint
    from numpy import linspace
    import numpy as np

    dt = 0.01
    N = 500
    L = 1.
    x_0 = [1., 0.]
    T = linspace(0, N*dt, N)

    def x_dot(x, t):
        """Calculate the derivative of the pendulum in state space form.
        """

        x1 = x[0]
        x2 = x[1]

        dx1 = x2
        dx2 = -9.81/L*sin(x1)

        return [dx1, dx2]

    X = odeint(x_dot, x_0, T)

    plt.plot(T, X[:, 0], label=r"$\theta$ (rad)")
    plt.plot(T, X[:, 1], label=r"$\dot{\theta}$ (rad/s)")
    plt.title("Simulation with ODEINT")
    plt.xlabel("time (s)")
    plt.ylabel("trajectory")
    plt.legend()
    plt.savefig("pendulum_with_odeint.png")
    plt.show()
    plt.clf()

def main():
    import numpy as np
    T, X_1, X_2 = simulate_pendulum(x_0=[1., 0.], L=1., N=500, dt=0.01)
    plt.plot(T, X_1, label=r"$\theta$ (rad)")
    plt.plot(T, X_2, label=r"$\dot{\theta}$ (rad/s)")
    plt.title("Simulation with Euler")
    plt.xlabel("time (s)")
    plt.ylabel("trajectory")
    plt.legend()
    plt.savefig("pendulum_with_euler.png")
    plt.show()
    plt.clf()

if __name__ == "__main__":
    main()
    simulate_pendulum_odeint()
