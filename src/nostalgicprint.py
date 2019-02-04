#!/usr/bin/env python3
from pdf2image import convert_from_path
import img2pdf
import PyPDF2
from PIL import *
import image_slicer
import os
import sys
import multiprocessing
from joblib import Parallel, delayed
import time
from shutil import copyfile
import numpy as np
import argparse




new_image_name = "page_"
image_subfolder = "./temp/"
directory_content = ""
manual_file_name = ""
dpi_value = 100

def argparser():
    global manual_file_name
    global dpi_value
    
    parser = argparse.ArgumentParser(description='Exploit for vulnerability.')
    parser.add_argument('-f', '--file',type=argparse.FileType('r', encoding='UTF-8'), required=True, help='defines name of the manual file to be manipulated')
    parser.add_argument('-d', '--dpi', type=int,default=100,help='defines DPI of images extracted from manual file')
    args = parser.parse_args()
    
    manual_file_name = args.file.name
    dpi_value = args.dpi

    print("[+] Setting manual file name to: %s" % manual_file_name)
    print("[+] Setting DPI to %d" % dpi_value)


def save_page_as_pdf(page,i):
    global new_image_name
    print("\t[+] Saving page %d as %s" % (i, "page_"+str("%02d" % i)+".png") )
    page.save(image_subfolder + new_image_name+str("%02d" % i)+".png","PNG")


def read_pdf_page_by_page(filename,user_dpi=300):
    global directory_content
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

    directory_content = os.listdir(image_subfolder)
    directory_content.sort()
    print("[+] Type(directory_content): ", type(directory_content))
    print("[+] Directory_content: ",directory_content)
    print("[+] Len(directory_content", len(directory_content) )
    print("[-] range: ", (len(directory_content) // 2))

    #check if merge works correctly by checking if image number is multiple of 2
    if len(directory_content) % 2 != 0:
        print("[-] Number of images no multiple of 2 - cannot merge")
        sys.exit(-1)

    Parallel(n_jobs=num_cores)(delayed(open_file_and_merge)(i) for (i) in range((len(directory_content) // 2)))

    print("[+] Merging images into new_manual")
    with open("final_manual.pdf", "wb") as f:
        os.chdir(image_subfolder)
        directory_content_after_merge = os.listdir(os.getcwd())
        directory_content_after_merge.sort()
        f.write(img2pdf.convert([i for i in directory_content_after_merge if i.endswith(".png")]))
        os.chdir("..")

    rotate_pages_for_print("./final_manual.pdf")

def rotate_pages_for_print(filename):

    pdf_in = open(filename, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_in)
    pdf_writer = PyPDF2.PdfFileWriter()

    for pagenum in range(pdf_reader.numPages):
        page = pdf_reader.getPage(pagenum)
        if pagenum % 2:
            page.rotateClockwise(180)
        pdf_writer.addPage(page)

    pdf_out = open(filename, 'wb')
    pdf_writer.write(pdf_out)
    pdf_out.close()
    pdf_in.close()

def split_image(filename):
    print("\t[+] Splicing %s" % filename)
    image_slicer.slice(filename,2)
    #print("\t[+] Removing file: %s" % filename)
    os.remove(filename)

def open_file_and_merge(i):
    global directory_content
    page_left = image_subfolder + directory_content[i] #image_subfolder + new_image_name + str("%02d" % i) + ".png" 
    page_right = image_subfolder + directory_content[len(directory_content) -i-1] #image_subfolder + new_image_name + str("%02d" % (half_directory_count-i)) + ".png"
    if i%2 ==1:
        merge_images(page_left,page_right,i)
    else:
        merge_images(page_right,page_left,i)
# thanks to dermen for this solution
# https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python
def merge_images(page_left,page_right,i):
    print("\t[+] Merging: ('%s' , '%s')" % (page_left,page_right))


    list_im = [page_left,page_right]
    imgs    = [ Image.open(i) for i in list_im ]
    # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
    min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
    imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )

    # save that beautiful picture
    imgs_comb = Image.fromarray( imgs_comb)
    imgs_comb.save(image_subfolder + "merge_test"+ str("%02d" % i) +".png" )    
    os.remove(page_left)
    os.remove(page_right)

    # for a vertical stacking it is simple: use vstack
    #imgs_comb = np.vstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )
    #imgs_comb = PIL.Image.fromarray( imgs_comb)
    #imgs_comb.save( 'Trifecta_vertical.jpg' )

argparser()
read_pdf_page_by_page(manual_file_name,dpi_value)
