import numpy as np
import matplotlib.pyplot as plt
import copy
import time

def predict_linear_probs_1step(ts, xs, ys, dt, v_std_dev, beta_std_dev, K):
    cur_x, last_x = xs[1], xs[0]
    cur_y, last_y = ys[1], ys[0]
    cur_t = ts[1]
    
    vx = (xs[1] - xs[0]) / (ts[1] - ts[0])
    vy = (ys[1] - ys[0]) / (ts[1] - ts[0])
    v = np.sqrt(vx**2 + vy**2)
    vs = np.random.normal(v, v_std_dev, K)

    betas = np.random.normal(0, beta_std_dev, K)
    
    psi = np.arctan2(cur_y - last_y, cur_x - last_x)
    prob_points = []
    for k in range(K):
        r = vs[k] * dt
        dx = r * np.cos(psi + betas[k])
        x = dx + cur_x
        dy = r * np.sin(psi + betas[k])
        y = dy + cur_y
        t = dt + cur_t
        prob_points.append([t, x, y])

    if (K == 1):
        return prob_points
    else:
        return np.array(prob_points)

def predict_linear_probs_recursive(buffer, dt=None, v_std_dev=None, beta_std_dev=None, K=None):
    assert(buffer is None)
    assert(not dt is None)
    assert(not v_std_dev is None)
    assert(not beta_std_dev is None)
    assert(not K is None)
    started = False
    prob_points = []
    while True:
        if started:
            if buffer is None:
                ## No pose buffer. Extrapolate the last prob points for one step forward 
                ## An initial buffer is needed to start working:
                assert(len(prob_points != 0)) 
                next_prob_points = []
                for p in prob_points:
                    a_next_prob_point = predict_linear_probs_1step\
                        ([cur_t, p[0]], [cur_x, p[1]], [cur_y, p[2]], dt, v_std_dev, beta_std_dev, 1)
                    next_prob_points.append([a_next_prob_point[0][0], a_next_prob_point[0][1], a_next_prob_point[0][2]])
                prob_points = []
                prob_points = np.array(copy.deepcopy(next_prob_points))
            else:
                ## A pose buffer is passed. The prob points for one forward step must be returned
                ts = buffer[0]
                xs = buffer[1]
                ys = buffer[2]
                l = len(ts)
                assert(l == len(xs) == len(ys) == 2)
                cur_x = xs[1]
                cur_y = ys[1]
                cur_t = ts[1]
                prob_points = predict_linear_probs_1step(ts, xs, ys, dt, v_std_dev, beta_std_dev, K)
        else:
            started = True
        buffer = yield prob_points  


# Example usage
ts = [0.2, 0.3]  # Example time points
xs = [2, 3]  # Example x-coordinates
ys = [2, 3]  # Example y-coordinates
dt = 0.05  # Time step
v_std_dev = 1  # Velocity standard deviation
beta_std_dev = 10 * np.pi / 180  # Beta (angle) standard deviation
K = 100  # Number of probabilistic points

plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
gen = predict_linear_probs_recursive(None, dt, v_std_dev, beta_std_dev, K)
next(gen)
for n in range(1, 5):
    plt.cla()
    if (n == 1):
        prob_points = gen.send([ts, xs, ys])
    else:
        prob_points = next(gen)
    # Plot the probabilistic points
    for i in range(K):
        plt.scatter(prob_points[i, 1], prob_points[i, 2], alpha=0.2)
        # plt.plot(prob_points[:, i, 0], prob_points[:, i, 1], alpha=0.2)
    plt.scatter(xs, ys, color='red', label='Measured points')
    plt.legend()
    plt.title(f'Probabilistic 2D Path Extrapolation ({n} steps)')
    plt.pause(1)
