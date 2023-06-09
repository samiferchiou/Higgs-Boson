import numpy as np

#================================================================================================================#
#=============================================== HELPER FUNCTIONS ===============================================#
#================================================================================================================#

def compute_loss(y, tx, w):
    """Calculate the loss using mse cost function
    """
    e = y - tx @ w
    N = len(e)
    return e.T @ e / (2 * N)


def compute_rmse(y, tx, w):
    """compute the loss by mse."""
    w.flatten()
    e = y - tx @ w
    mse = e @ e / (2 * len(e))
    return np.sqrt(2 * mse)


def compute_gradient(y, tx, w):
    """Compute the gradient."""
    e = y - tx @ w
    N = len(e)
    return -1 / N * tx.T @ e


def compute_stoch_gradient(y, tx, w):
    """Compute a stochastic gradient from just few
    examples n and their corresponding y_n labels."""
    e = y - tx@w
    return -tx.T@e / len(e)


def sigmoid(t):
    """apply the sigmoid function on t."""
    return 1.0 / (1 + np.exp(-t))


def compute_loss_logistic(y, tx, w):
    """compute the loss: negative log likelihood."""
    y_hat = sigmoid(tx @ w)
    y_hat[y_hat == 1.0] = 0.999999999999
    y_hat[y_hat == 0.0] = 1e-20
    loss = (y.T @ np.log(y_hat)) + ((1 - y).T @ np.log(1 - y_hat))
    return np.squeeze(- loss)


def compute_gradient_logistic(y, tx, w):
    """compute the gradient of loss."""
    y_hat = sigmoid(tx.dot(w))
    grad = tx.T @ (y_hat - y.reshape((y.shape[0], 1)))
    return grad


def learning_by_gradient_descent(y, tx, w, gamma):
    """
    Do one step of gradient descen using logistic regression.
    Return the loss and the updated w.
    """
    loss = compute_loss_logistic(y, tx, w)
    #print(loss) # HERE
    grad = compute_gradient_logistic(y, tx, w)
    w -= gamma * grad
    return loss, w


def penalized_logistic_regression_one_iter(y, tx, w, lambda_):
    """return the loss, gradient"""
    norm_w = w.T @ w
    loss = compute_loss_logistic(y, tx, w) + lambda_ * norm_w
    norm_gradient = 2 * w
    gradient = compute_gradient_logistic(y, tx, w) + lambda_ * norm_gradient
    return loss, gradient


def learning_by_penalized_gradient_one_iter(y, tx, w, gamma, lambda_):
    """
    Do one step of gradient descent, using the penalized logistic regression.
    Return the loss and updated w.
    """
    loss, gradient = penalized_logistic_regression_one_iter(y, tx, w, lambda_)
    w = w - gamma * gradient
    return loss, w


def build_poly(x, degree):
    """polynomial basis functions for input data x, for j=0 up to j=degree.
    This function returns the matrix formed
    by applying the polynomial basis to the input data"""
    poly = np.ones((len(x), 1))
    for deg in range(1, degree+1):
        poly = np.c_[poly, np.power(x, deg)]
    return poly


def build_k_indices(y, k_fold, seed):
    """build k indices for k-fold."""
    num_row = y.shape[0]
    interval = int(num_row / k_fold)
    np.random.seed(seed)
    indices = np.random.permutation(num_row)
    k_indices = [indices[k * interval: (k + 1) * interval] for k in range(k_fold)]
    return np.array(k_indices)


def cross_validation_ridge(y, x, k_indices, k, lambda_, degree):
    """return the loss of ridge regression."""
    # get k'th subgroup in test, others in train
    te_indice = k_indices[k]
    tr_indice = k_indices[~(np.arange(k_indices.shape[0]) == k)]
    tr_indice = tr_indice.reshape(-1)
    x_tr = x[tr_indice]
    y_tr = y[tr_indice]
    x_te = x[te_indice]
    y_te = y[te_indice]

    # form data with polynomial degree
    tx_tr = build_poly(x_tr,degree)
    tx_te = build_poly(x_te,degree)

    # ridge regression
    w,_ = ridge_regression(y_tr, tx_tr, lambda_)

    # calculate the loss for train and test data
    loss_tr = compute_rmse(y_tr, tx_tr, w)
    loss_te = compute_rmse(y_te, tx_te, w)

    return loss_tr, loss_te


def cross_validation_demo_ridge(y, x, seed, degrees, k_fold, lambdas):
    # split data in k fold
    k_indices = build_k_indices(y, k_fold, seed)
    # define lists to store the loss of test data and best lambda
    best_rmses = []
    best_lambdas = []

    for degree in degrees:
        rmse_te = []
        # cross validation
        for lambda_ in lambdas:
            rmse_te_tmp = []
            for k in range(k_fold):
                _, loss_te = cross_validation_ridge(y, x, k_indices, k, lambda_, degree)
                rmse_te_tmp.append(loss_te)
            rmse_te.append(np.mean(rmse_te_tmp))

        ind_best_lambda = np.argmin(rmse_te)
        best_lambdas.append(lambdas[ind_best_lambda])
        best_rmses.append(rmse_te[ind_best_lambda])
        #print(f"    min loss for a {degree} polynomial expansion feature = {min(rmse_te)}")

    ind_best_degree =  np.argmin(best_rmses)

    best_degree = degrees[ind_best_degree]
    best_lambda = best_lambdas[ind_best_degree]
    return best_degree, best_lambda


def cross_validation_logistic(y, x, max_iters, k_indices, k, gamma, degree):
    """return the loss of ridge regression."""
    # get k'th subgroup in test, others in train
    te_indice = k_indices[k]
    tr_indice = k_indices[~(np.arange(k_indices.shape[0]) == k)]
    tr_indice = tr_indice.reshape(-1)

    x_tr = x[tr_indice]
    y_tr = y[tr_indice]
    x_te = x[te_indice]
    y_te = y[te_indice]

    # form data with polynomial degree
    tx_tr = build_poly(x_tr,degree)
    tx_te = build_poly(x_te,degree)

    # logistic regression
    w,_ = logistic_regression(y_tr, tx_tr, max_iters, gamma)

    # calculate the loss for train and test data
    loss_tr = compute_loss_logistic(y_tr, tx_tr, w)
    loss_te = compute_loss_logistic(y_te, tx_te, w)

    return loss_tr, loss_te


def cross_validation_demo_logistic(y, x, max_iters, seed, degrees, k_fold, gammas):
    # split data in k fold
    k_indices = build_k_indices(y, k_fold, seed)
    # define lists to store the loss of test data and gamma
    best_rmses = []
    best_gammas = []

    for degree in degrees:
        rmse_te = []
        # cross validation
        for gamma in gammas:
            rmse_te_tmp = []
            for k in range(k_fold):
                _,loss_te = cross_validation_logistic(y, x, max_iters, k_indices, k, gamma, degree)
                rmse_te_tmp.append(loss_te)
            #print(rmse_te_tmp)
            rmse_te.append(np.mean(rmse_te_tmp))

        ind_best_gamma = np.argmin(rmse_te)
        best_gammas.append(gammas[ind_best_gamma])
        best_rmses.append(rmse_te[ind_best_gamma])

    ind_best_degree =  np.argmin(best_rmses)
    best_degree = degrees[ind_best_degree]
    best_gamma = best_gammas[ind_best_degree]
    print(f"##### {best_rmses} ####")

    return best_degree, best_gamma, min(best_rmses)


def cross_validation_reg_logistic(y, x, max_iters, k_indices, k, lambda_, gamma, degree):
    """return the loss of ridge regression."""
    # get k'th subgroup in test, others in train
    te_indice = k_indices[k]
    tr_indice = k_indices[~(np.arange(k_indices.shape[0]) == k)]
    tr_indice = tr_indice.reshape(-1)
    x_tr = x[tr_indice]
    y_tr = y[tr_indice]
    x_te = x[te_indice]
    y_te = y[te_indice]

    # form data with polynomial degree
    tx_tr = build_poly(x_tr,degree)
    tx_te = build_poly(x_te,degree)
    initial_w = np.zeros((tx_tr.shape[1],1))

    # regularized logistic regression
    w,_ = reg_logistic_regression(y_tr, tx_tr, lambda_, initial_w, max_iters, gamma)

    # calculate the loss for train and test data
    loss_tr = compute_loss_logistic(y_tr, tx_tr, w)
    loss_te = compute_loss_logistic(y_te, tx_te, w)

    return loss_tr, loss_te

def cross_validation_demo_reg_logistic(y, x, max_iters, seed, degrees, k_fold, lambdas, gammas):
    # split data in k fold
    k_indices = build_k_indices(y, k_fold, seed)
    # define lists to store the loss of test data, gamma and lambda
    best_rmses = []
    best_gammas = []
    best_lambdas = []

    for degree in degrees:
        rmse_te_lambda = []
        # cross validation
        for lambda_ in lambdas:
            rmse_te_gamma = []
            for gamma in gammas:
                rmse_te_k = []
                for k in range(k_fold):
                    _, loss_te = cross_validation_reg_logistic(y, x, max_iters, k_indices, k, lambda_, gamma, degree)
                    rmse_te_k.append(loss_te)
                rmse_te_gamma.append(np.mean(rmse_te_k))

            ind_best_gamma = np.argmin(rmse_te_gamma)
            best_gammas.append(gammas[ind_best_gamma])
            rmse_te_lambda.append(rmse_te_gamma[ind_best_gamma])

        ind_best_lambda = np.argmin(rmse_te_lambda)
        best_lambdas.append(lambdas[ind_best_lambda])
        best_rmses.append(rmse_te_lambda[ind_best_lambda])

    ind_best_degree =  np.argmin(best_rmses)

    best_degree = degrees[ind_best_degree]
    best_gamma = best_gammas[ind_best_degree]
    best_lambda = best_lambdas[ind_best_degree]

    return best_degree, best_gamma, best_lambda


def batch_iter(y, tx, batch_size, num_batches=1, shuffle=True):#
    """
    Generate a minibatch iterator for a dataset.
    Takes as input two iterables (here the output desired values 'y' and the input data 'tx')
    Outputs an iterator which gives mini-batches of `batch_size` matching elements from `y` and `tx`.
    Data can be randomly shuffled to avoid ordering in the original data messing with the randomness of the minibatches.
    Example of use :
    for minibatch_y, minibatch_tx in batch_iter(y, tx, 32):
        <DO-SOMETHING>
    """
    data_size = len(y)

    if shuffle:
        shuffle_indices = np.random.permutation(np.arange(data_size))
        shuffled_y = y[shuffle_indices]
        shuffled_tx = tx[shuffle_indices]
    else:
        shuffled_y = y
        shuffled_tx = tx
    for batch_num in range(num_batches):
        start_index = batch_num * batch_size
        end_index = min((batch_num + 1) * batch_size, data_size)
        if start_index != end_index:
            yield shuffled_y[start_index:end_index], shuffled_tx[start_index:end_index]




#================================================================================================================#
#================================================ MAIN FUNCTIONS ================================================#
#================================================================================================================#

def least_squares_GD(y, tx, initial_w, max_iters, gamma):
    """Gradient descent algorithm."""
    w = initial_w
    for n_iter in range(max_iters):
        #computing the gradient of the loss function
        grad = compute_gradient(y, tx, w)
        #iteratively updating the weights w w.r. to the gradient
        w = w - gamma * grad
    loss = compute_loss(y, tx, w)
    return w, loss


def least_squares_SGD(y, tx, initial_w, batch_size, max_iters, gamma):
    """Stochastic gradient descent algorithm."""
    w = initial_w
    for n_iter in range(max_iters):
        for y_batch, tx_batch in batch_iter(y, tx, batch_size=batch_size, num_batches=1):
            # compute a stochastic gradient and loss
            grad = compute_stoch_gradient(y_batch, tx_batch, w)
            # update w through the stochastic gradient update
            w = w - gamma * grad
            # calculate loss
            # store w and loss
    loss = compute_loss(y, tx, w)
    return w, loss


def least_squares(y, tx):
    """calculate the least squares solution."""
    X = tx
    w = np.linalg.solve(X.T @ X, X.T @ y)
    loss = compute_loss(y, X, w)
    return w, loss


def ridge_regression(y, tx, lambda_):
    """implement ridge regression."""
    X = tx
    N = X.shape[0]
    I = np.identity(X.shape[1])
    lambda_p = 2 * N * lambda_
    w = np.linalg.solve(X.T @ X + lambda_p * I, X.T @ y)
    loss = compute_loss(y, X, w)
    return w, loss


def logistic_regression(y, tx, initial_w, max_iters, gamma):
    w = initial_w
    threshold = 1e-8
    losses = []

    for iter in range(max_iters):
        loss, w = learning_by_gradient_descent(y, tx, w, gamma)
        losses.append(loss)
        # converge criterion
        if len(losses) > 1 and np.abs(losses[-1] - losses[-2]) < threshold:
            break
    return w, losses[-1]


def reg_logistic_regression(y, tx, lambda_, initial_w, max_iters, gamma):
    threshold = 1e-8
    losses = []
    w = initial_w

    # start the logistic regression
    for iter in range(max_iters):
        # get loss and update w.
        loss, w = learning_by_penalized_gradient_one_iter(y, tx, w, gamma, lambda_)
        # log info
        if iter % 1000 == 0:
            print("    Current iteration={i}, loss={l}".format(i=iter, l=loss))
        if iter == 9999:
            print("    Current iteration={i}, loss={l}".format(i=iter, l=loss))
        # converge criterion
        losses.append(loss)
        if len(losses) > 1 and np.abs(losses[-1] - losses[-2]) < threshold:
            break
    return w, losses[-1]
