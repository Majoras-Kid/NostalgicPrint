#!/usr/bin/env python3
from pdf2image import convert_from_path
from PIL import *
import image_slicer
import os
import sys
import multiprocessing
from joblib import Parallel, delayed
import time
from shutil import copyfile
import numpy as np


new_image_name = "page_"
image_subfolder = "./temp/"

def save_page_as_pdf(page,i):
    global new_image_name
    print("\t[+] Saving page %d as %s" % (i, "page_"+str("%02d" % i)+".png") )
    page.save(image_subfolder + new_image_name+str("%02d" % i)+".png","PNG")


def read_pdf_page_by_page(filename,user_dpi=300):
    if os.path.isdir(image_subfolder):
        print("[+] Storing images in folder: %s" % image_subfolder)
    else:
        print("[+] Creating subfolder: %s" % image_subfolder)
        os.makedirs(image_subfolder)

    print("[+] Opening file: %s" % filename)
    print("\t[+] Adjust Image DPI if it takes too long (current DPI=%d)" % user_dpi)
    start = time.time()
    pages = convert_from_path(filename,dpi=user_dpi)
    end = time.time()
    print("\t[+] Converting took %.2ds (%.2dm)" %(end - start, ((end - start)/60)))

    page_count = len(pages)

    print("[+] Starting to save images of %d pages" % page_count)
    num_cores = multiprocessing.cpu_count()
    #num_cores = 1
    start = time.time()
    Parallel(n_jobs=num_cores)(delayed(save_page_as_pdf)(page,i) for (i,page) in enumerate(pages))
    end = time.time()
    print("\t[!] Needed time to store pages: %.2ds (%.2dm)" %(end - start, ((end - start)/60)) )


    # copy first and last page into folder
    # this has to be done manually as the front and back are on separate sides

    print("[+] Starting to slice images")
    start = time.time()
    Parallel(n_jobs=num_cores)(delayed(split_image)(image_subfolder + new_image_name + str("%02d" % i) + ".png" ) for (i) in range(1,page_count-1))
    end = time.time()
    print("\t[!] Needed time to slice images: %.2ds (%.2dm)" %(end - start, ((end - start)/60)) )

    print("[+] Re-sorting and merging images")
    directory_content = os.listdir(image_subfolder).sort()
    print("[+] Directory_content: ",directory_content)
    print("[+] Len(directory_content", len(directory_content) )
    print("[-] range: ", (len(directory_content) // 2))

    #check if merge works correctly by checking if image number is multiple of 2
    if len(directory_content) % 2 != 0:
        print("[-] Number of images no multiple of 2 - cannot merge")
        sys.exit(-1)

    half_directory_count = len(directory_content) // 2
    for i in range((len(directory_content) // 2)):
        page_left = image_subfolder + directory_content[i] #image_subfolder + new_image_name + str("%02d" % i) + ".png" 
        page_right = image_subfolder + directory_content[len(directory_content) -i-1] #image_subfolder + new_image_name + str("%02d" % (half_directory_count-i)) + ".png"
        merge_images(page_left,page_right)
        
        if i > 1:
            return

def split_image(filename):
    print("\t[+] Splicing %s" % filename)
    image_slicer.slice(filename,2)
    #print("\t[+] Removing file: %s" % filename)
    os.remove(filename)

# thanks to dermen for this solution
# https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python
def merge_images(page_left,page_right):
    print("[+] Merging: ('%s' , '%s')" % (page_left,page_right))


    list_im = [page_left,page_right]
    imgs    = [ Image.open(i) for i in list_im ]
    # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
    min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
    imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )

    # save that beautiful picture
    imgs_comb = Image.fromarray( imgs_comb)
    imgs_comb.save(image_subfolder + "merge_test.png" )    

    # for a vertical stacking it is simple: use vstack
    #imgs_comb = np.vstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
    #imgs_comb = PIL.Image.fromarray( imgs_comb)
    #imgs_comb.save( 'Trifecta_vertical.jpg' )

read_pdf_page_by_page("./test2.pdf",user_dpi=10)
#split_image("./page_1.png")