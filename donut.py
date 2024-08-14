import pygame
import time
import math
import sys
import numpy as np

pygame.init()

blue = pygame.Color((13, 29, 166))
grey = pygame.Color((127,127,127))
black = pygame.Color((0,0,0))
white = pygame.Color((255,255,255))

screen = pygame.display.set_mode((1000,800))
pygame.display.set_caption('Spinning_Donut')

# Moving the donut to the center of the screen
def center(x, y):
    return (x+500, y+400)

# Casting a 3D donut onto a 2D screen. Tuning the k parameters allows to fit the whole donut on the screen
def projection(point,k):
    x = point[0]
    y = point[1]
    z = point[2] + 480
    return ((k*x)/z, (k*y)/z, z)

# Generating the points for the cross-section of the donut
def base_sphere(r_small, r_big, n_points):
    theta = list(range(n_points))
    c = 2 * math.pi / n_points
    theta = [x * c for x in theta]
    x = r_big + r_small * np.cos(theta)
    y = r_small * np.sin(theta)
    z = [0] * n_points
    x_n = np.cos(theta)
    y_n = np.sin(theta)
    z_n = [0] * n_points
    return {'points': np.array(list(zip(x,y,z))), 'normals': np.array(list(zip(x_n,y_n,z_n)))}

# Generating the whole donut by rotating the points in the cross-section
def torus(sphere_points,n_points):
    phi = list(range(n_points))
    c = 2 * math.pi / n_points
    phi = [x * c for x in phi]
    final_torus = [] 
    final_normals = []
    for p in phi:
        rotation = np.array([[np.cos(p),0,np.sin(p)],[0,1,0],[-np.sin(p),0,np.cos(p)]])
        new_points = np.matmul(sphere_points.get('points'),rotation)
        new_normals = np.matmul(sphere_points.get('normals'),rotation)
        final_torus.extend(new_points)
        final_normals.extend(new_normals)
    return {'points': np.array(final_torus), 'normals': np.array(final_normals)}

# The "spin" in the spinning donut
def rotate(torus_points):
    points = torus_points.get('points')
    normals = torus_points.get('normals')
    c1 = 0.00005*math.pi
    c2 = 0.00001*math.pi
    # m1 = np.array([[1,0,0],[0,np.cos(c1),np.sin(c1)],[0,-np.sin(c1),np.cos(c1)]])
    m1 = np.array([[np.cos(c2),0,np.sin(c2)],[0,1,0],[-np.sin(c2),0,np.cos(c2)]])

    new_points = np.matmul(points,m1)
    # new_points = np.matmul(new_points,m2)
    new_normals = np.matmul(normals,m1)
    # new_normals = np.matmul(new_normals,m2)

    return {'points': new_points, 'normals': new_normals}

# Correction of the donut position so that we see it from the front and not from below
def rotate_once(torus_points):
    points = torus_points.get('points')
    normals = torus_points.get('normals')
    c1 = 0.5*math.pi
    m1 = np.array([[1,0,0],[0,np.cos(c1),np.sin(c1)],[0,-np.sin(c1),np.cos(c1)]])

    new_points = np.matmul(points,m1)
    new_normals = np.matmul(normals,m1)

    return {'points': new_points, 'normals': new_normals}
    
# Each Point in the donut is 5 pixels by 5 pixels.
def snap_to_grid(x,y):
    return ((x//5)*5,(y//5)*5)

# Printing a point to the screen
def render_char(x,y, brightness):
    new_x, new_y = x, y 
    new_x += (5 - brightness) // 2        
    new_y += (5 - brightness) // 2        
    pygame.draw.rect(screen, white, (new_x, new_y, brightness, brightness))

def round_up_to_even(f):
    return math.ceil(f / 2.) * 2

def main():
    light_direction = np.array([0,math.sqrt(0.5),-math.sqrt(0.5)]) #Light coming from behind and below the screen
    screen.fill((grey))
    t = torus(base_sphere(150,250, 30),60)
    t = rotate_once(t)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill(black)
        points = t.get('points')
        count = 0
        for p in points:
            # print(count, p)
            count += 1
        normals = t.get('normals')
        taken = {}
        for i in range(len(points)):
            brightness = np.dot(normals[i],light_direction)
            brightness = max(0, brightness)
            brightness *= 5 
            x, y, depth = projection(points[i], 250)
            x, y = center(x,y)
            x, y = snap_to_grid(x,y)
            if (x,y) not in taken.keys():
                render_char(x,y,brightness)
                taken[(x,y)] = depth
            elif depth < taken.get((x,y)):
                pygame.draw.rect(screen, black, (x, y, 5, 5))
                render_char(x,y,round_up_to_even(brightness))
                taken[(x,y)] = depth
            t = rotate(t)

        pygame.display.update()
        # time.sleep(1/24)

if __name__ == '__main__':

    main()
