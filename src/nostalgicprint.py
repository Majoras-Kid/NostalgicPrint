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
    
    parser = argparse.ArgumentParser(description='File manipulation to create a manual booklet of Nintendo games')
    parser.add_argument('-f', '--file',type=argparse.FileType('r', encoding='UTF-8'), required=True, help='defines name of the manual file to be manipulated')
    parser.add_argument('-d', '--dpi', type=int,default=100,help='defines DPI of images extracted from manual file')
    
    args = parser.parse_args()
    
    manual_file_name = args.file.name
    dpi_value = args.dpi

    if dpi_value < 0:
        print("[-] Negative DPI values cannot be used")
        sys.exit(-1)

    print("\t[+] Setting manual file name to: %s" % manual_file_name)
    print("\t[+] Setting DPI to %d" % dpi_value)


def save_page_as_png(page,i):
    global new_image_name
    print("\t[+] Saving page %d as %s" % (i, "page_"+str("%03d" % i)+".png") )
    page.save(image_subfolder + new_image_name+str("%03d" % i)+".png","PNG")


def read_pdf_page_by_page(filename,user_dpi=300):
    global directory_content
    global image_subfolder
    global new_image_name
    #check if a temporary subfolder exists, if not create it
    #this subfolder will contain the sliced and merged pages
    #but will be cleaned up at the end of the program
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
    page_count = len(pages)
    print("\t[+] Converting took %.2ds (%.2dm)" %(end - start, ((end - start)/60)))

    


    print("[+] Starting to save images of %d pages" % page_count)
    num_cores = multiprocessing.cpu_count()
    #num_cores = 1
    start = time.time()
    Parallel(n_jobs=num_cores)(delayed(save_page_as_png)(page,i) for (i,page) in enumerate(pages))
    end = time.time()
    print("\t[!] Needed time to store pages: %.2ds (%.2dm)" %(end - start, ((end - start)/60)) )



    print("[+] Starting to slice images")
    start = time.time()
    Parallel(n_jobs=num_cores)(delayed(split_image)(image_subfolder + new_image_name + str("%03d" % i) + ".png" ) for (i) in range(1,page_count-1))
    end = time.time()
    print("\t[!] Needed time to slice images: %.2ds (%.2dm)" %(end - start, ((end - start)/60)) )



    print("[+] Re-sorting and merging images per page")
    start = time.time()
    directory_content = os.listdir(image_subfolder)
    directory_content.sort()

    #check if merge works correctly by checking if image number is multiple of 2
    if len(directory_content) % 2 != 0:
        print("\t[-] Number of images no multiple of 2 - cannot merge")
        sys.exit(-1)

    Parallel(n_jobs=num_cores)(delayed(open_file_and_merge)(i) for (i) in range((len(directory_content) // 2)))
    end = time.time()
    print("\t[!] Needed time to sort and merge images per page: %.2ds (%.2dm)" %(end - start, ((end - start)/60)) )



    print("[+] Merging pages into final manual")
    start = time.time()
    with open("manual.pdf", "wb") as f:
        os.chdir(image_subfolder)
        directory_content_after_merge = os.listdir(os.getcwd())
        directory_content_after_merge.sort()
        #print("[+] directory_content_after_merge",directory_content_after_merge)
        f.write(img2pdf.convert([i for i in directory_content_after_merge if i.endswith(".png")]))
        f.close()
    os.chdir("..")

    rotate_pages_for_print("./manual.pdf")
    end = time.time()
    print("\t[!] Needed time to create final pdf file: %.2ds (%.2dm)" %(end - start, ((end - start)/60)) )



    print("[+] Deleting temporary files in %s" % image_subfolder)
    start = time.time()
    for the_file in os.listdir(image_subfolder):
        file_path = os.path.join(image_subfolder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)    
    end = time.time()
    os.remove("./manual.pdf")
    print("\t[!] Needed time to delete temporary files: %.2ds (%.2dm)" %(end - start, ((end - start)/60)) )


#in order to print Double-sided the backside (-> every second page) has to be flipped 180 degree
def rotate_pages_for_print(filename):

    pdf_in = open(filename, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_in)
    pdf_writer = PyPDF2.PdfFileWriter()

    for pagenum in range(pdf_reader.numPages):
        page = pdf_reader.getPage(pagenum)
        if pagenum % 2:
            page.rotateClockwise(180)
        pdf_writer.addPage(page)

    pdf_out = open("final_manual.pdf", 'wb')
    pdf_writer.write(pdf_out)
    pdf_out.close()
    pdf_in.close()
    

#spliting the original page into two frames of same size
#these image parts are then re-ordered
def split_image(filename):
    print("\t[+] Slicing %s" % filename)
    image_slicer.slice(filename,2)
    #print("\t[+] Removing file: %s" % filename)
    os.remove(filename)

#select and merge two images into a new page
#use parameter 'i' to sort new pages in the final pdf
def open_file_and_merge(i):
    global directory_content
    page_left = image_subfolder + directory_content[i]
    page_right = image_subfolder + directory_content[len(directory_content) -i-1]
    if i%2 ==1:
        merge_images(page_left,page_right,i)
    else:
        merge_images(page_right,page_left,i)


#execute image merge
#images are merged horizontal
# thanks to dermen for this solution
# https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python
def merge_images(page_left,page_right,i):
    #print("\t[+] Merging: ('%s' , '%s')" % (page_left,page_right))
    list_im = [page_left,page_right]
    imgs    = [ Image.open(i) for i in list_im ]
    # pick the image which is the smallest, and resize the others to match it (can be arbitrary image shape here)
    min_shape = sorted( [(np.sum(i.size), i.size ) for i in imgs])[0][1]
    imgs_comb = np.hstack( (np.asarray( i.resize(min_shape) ) for i in imgs ) )

    # save that beautiful picture
    imgs_comb = Image.fromarray( imgs_comb)
    imgs_comb.save(image_subfolder + "merge_test"+ str("%03d" % i) +".png" )    
    os.remove(page_left)
    os.remove(page_right)


argparser()
read_pdf_page_by_page(manual_file_name,dpi_value)
