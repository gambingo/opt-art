import random
import pickle
from os import path
from pathlib import Path

from rtree import index
from PIL import Image, ImageDraw


class Stipple:
    def __init__(self, original_filename=None, greyscale_filename=None):
        if original_filename:
            self.original_filename = original_filename
            self.original_img = Image.open(original_filename)
            self.img = self.make_greyscale()

        elif greyscale_filename:
            self.img = Image.open(greyscale_filename)
            self.greyscale_filename = greyscale_filename

        # Initalize empty variables
        self.pixel_coords = None
        self.darkness_values = None
        self.chosen_points = []
        self.rtree_idx = index.Index()
        self.iteration_count = 0


    def make_greyscale(self, save_greyscale=True):
        img = self.original_img.convert("LA")
        if save_greyscale:
            self.filename_greyscale = self.original_filename.split(".png")[0] + "_greyscale.png"
            img.save(Path(self.filename_greyscale))
        return img


    def stipple(self, k=200, iterations=200):
        self.get_index_and_darkness_vals()
        self.place_dots(k)
        self.redistribute_dots(iterations)
        img = self.draw_points()
        return img


    def get_index_and_darkness_vals(self):
        width, height = self.img.size
        pixel_coords = [None]*width*height

        ii = 0
        for w in range(width):
            for h in range(height):
                pixel_coords[ii] = (w, h, 0)  # (x, y, n)
                ii += 1
                
        # 0 is black, 255 is white
        pixels = list(self.img.getdata())
        darkness_values = [(255-p[0])/p[1] for p in pixels]
        self.pixel_coords = pixel_coords
        self.darkness_values = darkness_values


    def place_dots(self, k):
        """
        Place the initial points or add additional points
        ---
        k (int):    Number of points to plot  
        """
        if self.pixel_coords is None or self.darkness_values is None:
            self.get_index_and_darkness_vals()

        N = len(self.chosen_points)
        rtree_idx = self.rtree_idx

        additional_points = random.choices(self.pixel_coords, weights=self.darkness_values, k=k)
        for ii, p in enumerate(additional_points):
            x, y = p[0], p[1]
            rtree_idx.insert(N + ii, (x, y, x, y))  # left, bottom, right, top

        self.chosen_points = self.chosen_points + additional_points


    def redistribute_dots(self, iterations=1000):
        """Distribute dots with the 'Tractor Beam' Method"""
        for _ in range(iterations):
            w = random.choices(self.pixel_coords, weights=self.darkness_values, k=1)[0]
            w_x, w_y = w[0], w[1]

            p_id = list(self.rtree_idx.nearest((w_x, w_y, w_x, w_y), 1))[0]
            p = self.chosen_points[p_id]
            p_x, p_y, n = p[0], p[1], p[2]

            # Pull it with the tractor beam!
            x_new = (1/(n+1)*w_x) + (n/(n+1)*p_x)
            y_new = (1/(n+1)*w_y) + (n/(n+1)*p_y)
            n = n+1

            # Move point
            self.chosen_points[p_id] = (x_new, y_new, n)
            self.rtree_idx.delete(p_id, (p_x, p_y, p_x, p_y))
            self.rtree_idx.insert(p_id, (x_new, y_new, x_new, y_new))
            self.iteration_count += 1


    def draw_points(self, save_image=False, radius=None, include_coords=False, include_ids=False):
        """Place them dots!"""
        self.dot_img = Image.new('RGB', self.img.size, color=(255,255,255,0))
        draw = ImageDraw.Draw(self.dot_img)
        
        if radius:
            for p in self.chosen_points:
                # Approximate a circle
                draw.regular_polygon((p[1], p[0], radius), n_sides=30, fill="black")
        else:
            draw.point([(p[1], p[0]) for p in self.chosen_points], fill="black")

        if include_ids:
            for ii, p in enumerate(self.chosen_points):
                draw.text((p[1], p[0]), f"{ii}", fill="black")

        if include_coords:
            for p in self.chosen_points:
                draw.text((p[1], p[0]), f"({p[1]}, {p[0]})", fill="black")

        if save_image:
            k = len(self.chosen_points)
            n = self.iteration_count
            self.filename_points = self.original_filename.split(".png")[0] + \
                f"_{k}_points" + f"_{n}_.png"
            self.dot_img.save(Path(self.filename_points))
        return self.dot_img


    def save(self, filename):
        pickle.dump(self, open("filename", "wb"))


if __name__ == "__main__":
    pass