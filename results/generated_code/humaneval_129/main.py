def minPath(grid, k):
    N = len(grid)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def dfs(x, y, path, steps):
        if steps == k:
            return path[:]
        min_path = None
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N:
                new_path = dfs(nx, ny, path + [grid[nx][ny]], steps + 1)
                if min_path is None or (new_path is not None and len(new_path) < len(min_path)):
                    min_path = new_path
        return min_path

    min_path = None
    for i in range(N):
        for j in range(N):
            path = dfs(i, j, [grid[i][j]], 1)
            if min_path is None or (path is not None and len(path) < len(min_path)):
                min_path = path
    return min_path