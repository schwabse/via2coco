import os
import cv2
import datetime
import json
import getArea


def create_image_info(image_id, file_name, image_size,
                      date_captured=datetime.datetime.utcnow().isoformat(' '),
                      license_id=1, coco_url="", flickr_url=""):

    image_info = {
            "id": image_id,
            "file_name": file_name,
            "width": image_size[0],
            "height": image_size[1],
            "date_captured": date_captured,
            "license": license_id,
            "coco_url": coco_url,
            "flickr_url": flickr_url
    }

    return image_info


def create_annotation_info(annotation_id, image_id, category_id, is_crowd,
                           area, bounding_box, segmentation):

    annotation_info = {
        "id": annotation_id,
        "image_id": image_id,
        "category_id": category_id,
        "iscrowd": is_crowd,
        "area": area,# float
        "bbox": bounding_box,# [x,y,width,height]
        "segmentation": segmentation# [polygon]
    }

    return annotation_info


def get_segmenation(coord_x, coord_y):
    seg = []
    for x, y in zip(coord_x, coord_y):
        seg.append(x)
        seg.append(y)
    return [seg]


def convert(imgdir, annpath):
    '''
    :param imgdir: directory for your images
    :param annpath: path for your annotations
    :return: coco_output is a dictionary of coco style which you could dump it into a json file
    as for keywords 'info','licenses','categories',you should modify them manually
    '''

    coco_output = {}
    coco_output['info'] = {
        "description": "Example Dataset",
        "url": "https://triasoft.wordpress.com/",
        "version": "0.1.0",
        "year": 2019,
        "contributor": "schwabse",
        "date_created": datetime.datetime.utcnow().isoformat(' ')
    }
    coco_output['licenses'] = [
        {
            "id": 1,
            "name": "Attribution-NonCommercial-ShareAlike License",
            "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/"
        }
    ]
    coco_output['categories'] = [{
        'id': 1,
        'name': 'vertebrae',
        'supercategory': 'spine',
    },
        {
            'id': 2,
            'name': 'vertebrae',
            'supercategory': 'spine',
        }
    ]
    coco_output['images'] = []
    coco_output['annotations'] = []

    ann = json.load(open(annpath))
    # annotations id start from zero
    ann_id = 0

    # in VIA annotations, keys are image name
    for img_id, key in enumerate(ann.keys()):

        filename = ann[key]['filename']
        img = cv2.imread(imgdir+filename)

        # make image info and storage it in coco_output['images']
        image_info = create_image_info(img_id, os.path.basename(filename), img.shape[:2])
        coco_output['images'].append(image_info)

        regions = ann[key]["regions"]
        # for one image ,there are many regions,they share the same img id
        for region in regions:

            cur = regions[region]

            try:
                cat = cur['region_attributes']['label']
                print(cat)
                assert cat in ['vertebrae', 'S']
            except:
                cat = ''

            if cat == 'rib':
                cat_id = 1
            else:
                cat_id = 2
            iscrowd = 0

            points_x = cur['shape_attributes']['all_points_x']
            points_y = cur['shape_attributes']['all_points_y']
            area = getArea.GetAreaOfPolyGon(points_x, points_y)
            min_x = min(points_x)
            max_x = max(points_x)
            min_y = min(points_y)
            max_y = max(points_y)
            box = [min_x, min_y, max_x-min_x, max_y-min_y]
            segmentation = get_segmenation(points_x, points_y)

            # make annotations info and storage it in coco_output['annotations']
            ann_info = create_annotation_info(ann_id, img_id, cat_id, iscrowd, area, box, segmentation)
            coco_output['annotations'].append(ann_info)
            ann_id = ann_id + 1
            
    return coco_output

str_path_to_via_file = '/test.json'
str_path_to_images = '/'
wd = os.getcwd()

path_via = os.path.join(wd + str_path_to_via_file)
path_img = os.path.join(wd + str_path_to_images)

coco_json = convert(path_img, path_via )

with open('output.json', 'w') as outfile:
    json.dump(coco_json, outfile)

print('Sucessfully dumped in ' + wd + '\output.json \n')
print(coco_json)