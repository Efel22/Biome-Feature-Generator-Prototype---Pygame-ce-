import math
import random
import noise # type: ignore
import numpy as np # type: ignore

# This file will hold diverse world gen instructions that manipulate
# received arrays and transform them according to the different
# algorithms

# Function used by the generation functions
def getDist(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


# * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * CHANCE GENERATION * * * * * * * 
# * * * * * * * * * * * * * * * * * * * * * * *
def wrlGen_Chance(arr, tileId, chance):

    """
    Generates a value based on a provided chance (percentage form).

    Parameters:
        arr (list of list): The 2D array to modify.
        tileId (string): The value to place along the path.
        chance (int): The chance of placing a tileId.
    """

    # Validate chance_percent
    if not (0 <= chance <= 100):
        chance = 0

    for row in range(len(arr)):
        for col in range(len(arr)):

            # Check if the random chance succeeds
            if random.random() < (chance / 100):
                # Assign the tileId to the randomly selected cell
                arr[row][col] = tileId

    return arr


# * * * * * * * * * * * * * * * * * * * * * * * 
# * * * * * * RAND POS GENERATION * * * * * * * 
# * * * * * * * * * * * * * * * * * * * * * * * 
def wrlGen_RandPos(arr, tileId, attempts):

    """
    Generate a value with X amount of tries randomly across the arr.

    Parameters:
        arr (list of list): The 2D array to modify.
        tileId (string): The value to place.
        attempts (int): Total amount of attempts of placement for the tileId.
    """

    # Get the length of the array once
    lengthOfArr = len(arr)
    
    # For each specified try
    for _ in range(attempts):
        # Generate random coordinates
        rand_x = random.randint(0, lengthOfArr - 1)
        rand_y = random.randint(0, lengthOfArr - 1)
        
        # Assign the tileId to the randomly selected cell
        arr[rand_x][rand_y] = tileId

    return arr


# * * * * * * * * * * * * * * * *  * * * * * * * 
# * * * * * SPREAD RING GENERATION * * * * * * * 
# * * * * * * * * * * * * * * * *  * * * * * * * 
def wrlGen_SpreadRings(arr, tileId, amountOfRingsToPlace, minRingRadius, maxRingRadius, chanceOfPlacement = 100):

    """
    Generate X amount of Rings at X Location randomly spread.

    Parameters:
        arr (list of list): The 2D array to modify.
        tileId (string): The value to place.
        amountOfRingsToPlace (int): Amount of rings to place.
        minRingRadius (float): Minimum radius of the ring.
        maxRingRadius (float): Maximum radius of the ring.
        chanceOfPlacement (int): Chance of placing the tileId within the ring.
    """

    # For each amount of rings to place...
    for attempts in range(amountOfRingsToPlace):
                
        # Get the length of the arr
        lengthOfArr = len(arr)

        # Generate a list of random coords
        # Define coords vars
        rand_x = random.randint(0, lengthOfArr - 1)
        rand_y = random.randint(0, lengthOfArr - 1)
        randomPos = [rand_x,rand_y]

        # Gen the ring at the specified location
        arr = wrlGen_RingAt(arr, tileId, randomPos, minRingRadius, maxRingRadius, chanceOfPlacement)
    
    return arr


# * * * * * * * * * * * * * * * *  * * * * * * * 
# * * * * * * * RING AT GENERATION * * * * * * * 
# * * * * * * * * * * * * * * * *  * * * * * * * 
def wrlGen_RingAt(arr, tileId, ringPos, minRingRadius, maxRingRadius, chanceOfPlacement = 100):
    
    """
    Generates a ring at X position with Y Radius.

    Parameters:
        arr (list of list): The 2D array to modify.
        tileId (string): The value to place.
        ringPos (list): Where the ring's center is located.
        minRingRadius (float): Minimum radius of the ring.
        maxRingRadius (float): Maximum radius of the ring.
        chanceOfPlacement (int): Chance of placing the tileId within the ring.
    """

    for row in range(len(arr)):
        for col in range(len(arr)):
            
            # Place the tile if the dist. between the 
            # iterators (row & col) matches the radius
            # Also checks for the chance of placement
            dist = getDist(row, col, ringPos[0], ringPos[1])
            if minRingRadius <= dist <= maxRingRadius and ( random.random() < (chanceOfPlacement / 100) ):
                arr[row][col] = tileId

    return arr


# * * * * * * * * * * * * * * * * * * * * * * * 
# * * * * * * * WALL GENERATION * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * 
def wrlGen_Wall(arr, tileId, cardinalDir = "", initialWidth = 1, spreadDistance = 0, spreadInitialChance = 50, decayOfSpread = 2):

    """
    Generates a "wall" of the tileId on the specified direction. Can generate a "spread" of said tileId
    within X distance, an initialChance of placing the tileId, along with a decay variable that divides the
    initial chance each row loop.

    Parameters:
        arr (list of list): The 2D array to modify.
        tileId (string): The value to place along the path.
        cardinalDir (string): Determines where to place the "wall".
        initialWidth (int): Total width of the "wall".
        spreadDistance (int): How much does the "wall" spread outwards.
        spreadInitialChance (int): Initial chance of placing a tileId when spreading.
        decayOfSpread (float): Digit that divides the spreadInitialChance each row.
    """

    # First, create an entire "row" of the tileId
    otherArr = [[0 for _ in range(len(arr))] for _ in range(len(arr))]

    # Spread 
    # Do the spread code if the spreadDistance is more than 0 (it'd be unnecessary to execute the code)
    if spreadDistance > 0:
        start = initialWidth
        end = (initialWidth + spreadDistance)
        spreadInitialChance_new = spreadInitialChance

        for row in range(len(otherArr)):  # Ensure we don't go out of bounds
            for col in range(len(otherArr[row])):

                if row >= start and row <= end:

                    if random.random() < (spreadInitialChance_new / 100):
                        otherArr[row][col] = 1  # Assuming you want to set the value to 1

            # Apply decay to the spread chance for the next cell
            spreadInitialChance_new /= decayOfSpread


    # Wall Generation
    for row in range(len(otherArr)):
        for col in range(len(otherArr)):

            # if the row it is in matches the initial width,
            # set the cell to 1
            if row < initialWidth:
                otherArr[row][col] = 1

    # Direction check
    if cardinalDir == "north":
        pass

    if cardinalDir == "south":
        flipped_array = otherArr[::-1]
        otherArr = flipped_array

    if cardinalDir == "east":
        rotated_array = [list(row) for row in zip(*otherArr[::-1])]
        otherArr = rotated_array

    if cardinalDir == "west":
        rotated_array = [list(row) for row in zip(*otherArr)][::-1]
        otherArr = rotated_array

     # Iterate over the finished randArr
    # to determine whether or not to place 
    # the tile or not
    for row in range(len(otherArr)):
        for col in range(len(otherArr)):

            if otherArr[row][col] == 1:
                arr[row][col] = tileId

    return arr

    pass


# * * * * * * * * * * * * * * * *  * * * * * * * 
# * * * * CELLULAR AUTOMATA GENERATION * * * * * 
# * * * * * * * * * * * * * * * *  * * * * * * * 
def wrlGen_Cellular(arr, tileId, tries = 1, amountOf1sRequired = 3, chanceOfPlacement = 100):

    """
    Uses a Cellular Automata algorithm to generate a value. It has a default of tries (1) and 
    amount of adjacent values of 3. 

    Parameters:
        arr (list of list): The 2D array to modify.
        tileId (string): The value to place along the path.
        tries (int): Amount of attempts to take place.
        amountOf1sRequired (int): Amount of adjacent alive cells to stay "alive".
        chanceOfPlacement (float): The probability (0 to 100) of placing a tileId at each step.
    """

    # Create an array filled with random 1s and 0s
    randArr = [[0 for _ in range(len(arr))] for _ in range(len(arr))]
    randArr = wrlGen_Chance(randArr, 1, 30)

    # DEBUG
    # print("randArr:")
    # printArr(randArr)
    # print("- - - - - - - - - - - - - ")
    # print("arr:")

    # For each try selected...
    for attempt in range(tries):
        # Create a copy of randArr to store the next state
        nextRandArr = [row[:] for row in randArr]

        for row in range(len(arr)):
            for col in range(len(arr)):

                # Create a var that holds the amount of 1s 
                # that are adjacent
                amountOf1s = 0

                # For each 1, check if another "1"
                # is adjacent

                # UP
                if row > 0:
                    if randArr[row - 1][col] == 1:
                        amountOf1s += 1

                    # UP - LEFT
                    if col > 0:
                        if randArr[row - 1][col - 1] == 1:
                            amountOf1s += 1

                    # UP - RIGHT
                    if col < len(arr) - 1:
                        if randArr[row - 1][col + 1] == 1:
                            amountOf1s += 1

                # DOWN
                if row < len(arr) - 1:
                    if randArr[row + 1][col] == 1:
                        amountOf1s += 1

                    # DOWN - LEFT
                    if col > 0:
                        if randArr[row + 1][col - 1] == 1:
                            amountOf1s += 1

                    # DOWN - RIGHT
                    if col < len(arr) - 1:
                        if randArr[row + 1][col + 1] == 1:
                            amountOf1s += 1

                # LEFT
                if col > 0:
                    if randArr[row][col - 1] == 1:
                        amountOf1s += 1

                # RIGHT
                if col < len(arr) - 1:
                    if randArr[row][col + 1] == 1:
                        amountOf1s += 1

                # If the # of 1s is 3 or more, then
                # that tile is "alive", thus its = 1
                # amountOf1sRequired by default = 3
                if amountOf1s >= amountOf1sRequired and (random.random() < (chanceOfPlacement / 100)):
                    nextRandArr[row][col] = 1

        # Update randArr to the next state
        randArr = nextRandArr

    # Iterate over the finished randArr
    # to determine whether or not to place 
    # the tile or not
    for row in range(len(randArr)):
        for col in range(len(randArr)):

            if randArr[row][col] == 1:
                arr[row][col] = tileId

    return arr
    

# * * * * * * * * * * * * * * * * * * * * * * *
# * * * * * * * PATH GENERATION * * * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * *
def wrlGen_Path(arr, tileId, startPos, endPos, radiusOfAttempt, chanceOfPlacement = 100, curveChance = 30):
    """
    Generates a path in a 2D array from startPos to endPos, placing tileId at each step.
    The path can curve randomly based on curveChance, with more variations.

    Parameters:
        arr (list of list): The 2D array to modify.
        tileId (string): The value to place along the path.
        startPos (tuple): The starting position (row, col).
        endPos (tuple): The ending position (row, col).
        radiusOfAttempt (int): Radius of the ring placed at each placement attempt.
        chanceOfPlacement (float): The probability (0 to 100) of placing a tileId at each step.
        curveChance (float): The probability (0 to 100) of deviating from the direct path.
    """
    rows = len(arr)
    cols = len(arr[0]) if rows > 0 else 0

    # Ensure start and end positions are within the array bounds
    if not (0 <= startPos[0] < rows and 0 <= startPos[1] < cols):
        raise ValueError("startPos is out of bounds.")
    if not (0 <= endPos[0] < rows and 0 <= endPos[1] < cols):
        raise ValueError("endPos is out of bounds.")

    # Initialize current position
    currentPos = list(startPos)

    # Continue until the current position reaches the end position
    while currentPos != list(endPos):
        # Place the tileId at the current position with a chance
        if random.random() < chanceOfPlacement:
            # arr[currentPos[0]][currentPos[1]] = tileId
            arr = wrlGen_RingAt(arr, tileId, [currentPos[0],currentPos[1]], 0, radiusOfAttempt, chanceOfPlacement)


        # Calculate the direction to move towards the end position
        deltaRow = endPos[0] - currentPos[0]
        deltaCol = endPos[1] - currentPos[1]

        # Introduce randomness to the direction (curving)
        if random.random() < curveChance:
            # Randomly adjust the direction more significantly
            deltaRow += random.randint(-radiusOfAttempt * 2, radiusOfAttempt * 2)
            deltaCol += random.randint(-radiusOfAttempt * 2, radiusOfAttempt * 2)
        else:
            # Small random adjustments to make the path less straight
            deltaRow += random.randint(-radiusOfAttempt, radiusOfAttempt)
            deltaCol += random.randint(-radiusOfAttempt, radiusOfAttempt)

        # Normalize the direction to ensure movement is within radiusOfAttempt
        stepRow = min(max(deltaRow, -radiusOfAttempt), radiusOfAttempt)
        stepCol = min(max(deltaCol, -radiusOfAttempt), radiusOfAttempt)

        # Update the current position
        currentPos[0] += stepRow
        currentPos[1] += stepCol

        # Ensure the new position is within bounds
        currentPos[0] = min(max(currentPos[0], 0), rows - 1)
        currentPos[1] = min(max(currentPos[1], 0), cols - 1)

    # Place the tileId at the end position
    arr[endPos[0]][endPos[1]] = tileId

    return arr


# * * * * * * * * * * * * * * *  * * * * * * * * 
# * * * * * * REPLACE GENERATION * * * * * * * * 
# * * * * * * * * * * * * * * *  * * * * * * * * 
def wrlGen_Replace(arr, tileId, tileToReplace, chance = 100):

    """
    Replaces X tile with Y based on the provided
    chance of placement

    Parameters:
        arr (list of list): The 2D array to modify.
        tileId (string): The value to place along the path.
        tileToReplace (string): Id. of the value to replace.
        chance (float): The probability (0 to 1) of placing a tileId at each step.
    """

    # Validate chance_percent
    if not (0 <= chance <= 100):
        chance = 0

    for row in range(len(arr)):
        for col in range(len(arr)):

            # Check if:
            # - cell matches tileToReplace
            # - the random chance succeeds
            if arr[row][col] == tileToReplace and ( random.random() < (chance / 100) ):
                # Assign the tileId to the randomly selected cell
                arr[row][col] = tileId

    return arr


# * * * * * * * * * * * * * * * * * * * * * * * * 
# * * * * * PERLIN NOISE GENERATION * * * * * * * 
# * * * * * * * * * * * * * * * * * * * * * * * * 
def wrlGen_PerlinNoise(arr, tileId, threshold, chanceOfPlacing = 100, scale = 15.0, octaves = 6, persistence = 0.5, lacunarity = 2.0, seed = 1):
    """
    Generates a 2D array of Perlin noise.

    Parameters:
        scale (float): Scaling factor for the noise.
        octaves (int): Number of octaves for the noise.
        persistence (float): Amplitude decay per octave.
        lacunarity (float): Frequency increase per octave.
        seed (int): Seed for the noise generation.

    Returns:
        2D array: A 2D array of the applied tileId with Perlin Noise.
    """
    width = len(arr)
    height = len(arr)

    world = np.zeros((height, width))

    for i in range(height):
        for j in range(width):
            world[i][j] = noise.pnoise2(
                i / scale,
                j / scale,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=width,
                repeaty=height,
                base=seed,
            )

    # Normalize the noise values to the range [0, 1]
    world = (world - np.min(world)) / (np.max(world) - np.min(world))

    """
    Sets array values to 1 where the noise is above the threshold.

    Parameters:
        noise_array (numpy.ndarray): A 2D array of Perlin noise values.
        threshold (float): Threshold value between 0 and 1.

    Returns:
        numpy.ndarray: A 2D array with values set to 1 where noise > threshold.
    """
    # Apply threshold
    result_array = (world > threshold).astype(int)

    # print(result_array)

    for row in range(len(result_array)):
        for col in range(len(result_array)):

            if result_array[row][col] == 1 and (random.random() < (chanceOfPlacing / 100)):
                arr[row][col] = tileId

    return arr


# * * * * * * * * * * * * * * * * * * * * * * * * 
# * * * MATCHING CONDITION GENERATION * * * * * *
# * * * * * * * * * * * * * * * * * * * * * * * * 
# Generate a value if the other array has a matching tileId at 
# a specific cell.
def wrlGen_MatchingTile(arr, tileId, arrToCompare, tileIdToCompare, chanceOfPlacement=100):
    """
    Generate a value in `arr` if the corresponding cell in `arrToCompare` matches `tileIdToCompare`.

    Parameters:
    - arr: The target array where the value will be placed.
    - tileId: The value to place in `arr` if the condition is met.
    - arrToCompare: The array to compare against.
    - tileIdToCompare: The tileId to match in `arrToCompare`.
    - chanceOfPlacement: The probability (0-100) of placing the tileId in `arr` if the condition is met.
    """
    
    # Iterate over each cell in the arrays
    for i in range(len(arr)):
        for j in range(len(arr)):
            # Check if the tileId in arrToCompare matches tileIdToCompare
            if arrToCompare[i][j] == tileIdToCompare:
                # Check if the tile should be placed based on the chanceOfPlacement
                if random.randint(1, 100) <= chanceOfPlacement:
                    arr[i][j] = tileId

    return arr


# def printArr(arr):
#     for row in arr:
#         print(" ".join(map(str, row)))

# for i in range(5):
#     arr = [[" " for _ in range(25)] for _ in range(25)]

#     # seed1 = random.randint(-10000, 10000)

#     arr = wrlGen_PerlinNoise(arr, "x", 0.5, seed=random.randint(-100, 100), scale=5, octaves=1)
#     printArr(arr)

#     print(" ")
#     print(" - - - - - - - - - - - - - - - - - - - - ")
#     print(" ")

