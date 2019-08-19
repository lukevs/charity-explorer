def batch(xs, batch_size):
    for i in range(0, len(xs), batch_size):
        yield xs[i:i+batch_size]
