using SimpleDirectMediaLayer
using Random

# Game constants
const WIDTH = 10
const HEIGHT = 20
const BLOCK_SIZE = 30
const WINDOW_WIDTH = WIDTH * BLOCK_SIZE
const WINDOW_HEIGHT = HEIGHT * BLOCK_SIZE
const TETROMINOES = [
    [[1, 1, 1, 1]],         # I-shape
    [[1, 1, 0], [0, 1, 1]], # Z-shape
    [[0, 1, 1], [1, 1, 0]], # S-shape
    [[1, 1], [1, 1]],       # O-shape
    [[1, 1, 1], [0, 1, 0]], # T-shape
    [[1, 1, 1], [1, 0, 0]], # L-shape
    [[1, 1, 1], [0, 0, 1]]  # J-shape
]

# Tetromino data type
struct Tetromino
    shape::Array{Int, 2}
    x::Int
    y::Int
end

# Initialize grid
function create_grid()
    return fill(0, HEIGHT, WIDTH)
end

# Add Tetromino to grid
function place_tetromino!(grid, tetromino)
    for i in 1:size(tetromino.shape, 1)
        for j in 1:size(tetromino.shape, 2)
            if tetromino.shape[i, j] == 1
                grid[tetromino.y + i - 1, tetromino.x + j - 1] = 1
            end
        end
    end
end

# Check if a tetromino fits in the grid
function valid_position(grid, tetromino)
    for i in 1:size(tetromino.shape, 1)
        for j in 1:size(tetromino.shape, 2)
            if tetromino.shape[i, j] == 1
                if tetromino.x + j - 1 < 1 || tetromino.x + j - 1 > WIDTH || tetromino.y + i - 1 > HEIGHT || tetromino.y + i - 1 < 1 || grid[tetromino.y + i - 1, tetromino.x + j - 1] == 1
                    return false
                end
            end
        end
    end
    return true
end

# Clear full lines and return the number of lines cleared
function clear_lines!(grid)
    full_lines = findall(row -> all(row .== 1), eachrow(grid))
    grid[full_lines, :] .= 0
    return length(full_lines)
end

# Rotate the tetromino
function rotate(tetromino)
    rotated_shape = reverse(tetromino.shape, dims=1)'  # Rotate 90 degrees clockwise
    return Tetromino(rotated_shape, tetromino.x, tetromino.y)
end

# Draw the grid and the tetromino
function draw_game(renderer, grid, tetromino)
    # Clear the screen
    set_render_draw_color(renderer, 0, 0, 0, 255)  # Black background
    render_clear(renderer)
    
    # Draw the grid
    set_render_draw_color(renderer, 200, 200, 200, 255)  # Light gray for blocks
    for y in 1:HEIGHT
        for x in 1:WIDTH
            if grid[y, x] == 1
                render_fill_rect(renderer, Rect((x - 1) * BLOCK_SIZE, (y - 1) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            end
        end
    end
    
    # Draw the current Tetromino
    set_render_draw_color(renderer, 0, 255, 0, 255)  # Green for current tetromino
    for i in 1:size(tetromino.shape, 1)
        for j in 1:size(tetromino.shape, 2)
            if tetromino.shape[i, j] == 1
                render_fill_rect(renderer, Rect((tetromino.x + j - 2) * BLOCK_SIZE, (tetromino.y + i - 2) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
            end
        end
    end
    
    render_present(renderer)
end

# Main game loop
function tetris_game()
    # Initialize SDL
    init(INIT_VIDEO)
    window = create_window("Tetris", WINDOWPOS_CENTERED, WINDOWPOS_CENTERED, WINDOW_WIDTH, WINDOW_HEIGHT, 0)
    renderer = create_renderer(window, -1, 0)

    grid = create_grid()
    current_tetromino = Tetromino(rand(TETROMINOES), Int(WIDTH / 2) - 1, 1)

    while true
        # Poll for events
        event = Event()
        while poll_event(event) != 0
            if event.type == QUIT
                return
            end
        end

        # Move the Tetromino down
        new_tetromino = Tetromino(current_tetromino.shape, current_tetromino.x, current_tetromino.y + 1)
        if valid_position(grid, new_tetromino)
            current_tetromino = new_tetromino
        else
            place_tetromino!(grid, current_tetromino)
            clear_lines!(grid)
            current_tetromino = Tetromino(rand(TETROMINOES), Int(WIDTH / 2) - 1, 1)
            if !valid_position(grid, current_tetromino)
                println("Game Over")
                break
            end
        end
        
        # Render the game state
        draw_game(renderer, grid, current_tetromino)
        delay(300)
    end

    destroy_renderer(renderer)
    destroy_window(window)
    quit()
end

# Run the game
tetris_game()
