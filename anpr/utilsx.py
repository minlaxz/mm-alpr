import cv2
import numpy as np


def get_projs(preprocessed_img):
    projs = np.sum(preprocessed_img, 1)
    m = np.max(projs)
    h, w = preprocessed_img.shape[:2]
    result = np.zeros((h, w))
    # Draw a line for each row
    for row in range(h):
        cv2.line(result, (0, row), (int(projs[row] * w / m), row), (255, 255, 255), 1)

    return (result, projs)
    # return projs


def sort_contours(cnts, reverse=False):
    i = 0
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    try:
        (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes) , key=lambda b: b[1][i], reverse=reverse))
    
    except ValueError: 
        print('bug utilsx@line 25.')
        pass

    return cnts
    # cnts = sorted(cnts, key=cv2.contourArea, reverse=reverse)
    # return cnts


def proj_points(dia_img, ratio=5, verbose=False):
    """
    small proj length means image is too small so we should not set bias that is too big
    that bias will cause indexing error
    so if proj is less than 100, it is supported to be small image so that bias will be set to 3
    fs is first starting point
    
    we want to crop a detected image based on horizontal image projection
    The idea is:
         first ending is set to be 1/5 of image plus bias
         first starting is set to bias
         second starting point is first ending point + bias / 2
         second ending point is 2/5 of image

    """
    _, projs = get_projs(dia_img)

    length_proj = len(projs)
    bias = length_proj / 25

    if True:
        # magic happened
        first_select_point = bias  # first select point with bias
        first_end_point = (length_proj / ratio) + bias  # (1 / ratio ) + bias
        second_select_point = first_end_point + bias / 2  # (1x / ratio ) + bias + bias / 2
        second_end_point =  (2 * length_proj / ratio) - bias  # (2x / ratio ) - bias

        if verbose:
            print("fs:{0}\tfe:{1}\ts:{2}\te:{3}".format(first_select_point, first_end_point, second_select_point, second_end_point))
        if verbose:
            print("lenproj", length_proj)

        first_min_pt = min(projs[int(first_select_point):int(first_end_point)])
        second_min_pt = min(projs[int(second_select_point):int(second_end_point)])

        if verbose:
            print(
                "first_min_pt:{}\t second_min_pt{}".format(first_min_pt, second_min_pt)
            )

        first_ref_pt = np.where(projs == first_min_pt)
        second_ref_pt = np.where(projs == second_min_pt)

        if verbose:
            print("first_ref_pt{}\tsecond_ref_pt{}".format(first_ref_pt, second_ref_pt))

        if len(second_ref_pt) < 30: # i know this is bug
            # narrow bandwidh
            second_ref_pt = list(range(second_ref_pt[0][0] - 5, second_ref_pt[0][0] + 5))

        if len(first_ref_pt) < 30:
            # narrow bandwidh
            first_ref_pt = list(range(first_ref_pt[0][0] - 5, first_ref_pt[0][0] + 5))

    return (first_ref_pt, second_ref_pt, projs)


def get_dia_kernel(lp_height):
    if 0 < lp_height <= 100 : return (1,1)
    elif 300 >= lp_height > 100 : return (3,3)
    elif lp_height > 300: return (5,5)
    else : return (0,0)


def get_blur_kernel(lp_height):
    if 0 < lp_height <= 100 : return (3,3)
    elif 300 >= lp_height > 100 : return (5,5)
    elif lp_height > 300: return (11,11)
    else : return (0,0)


def get_seg_char(lp_frame, verbose=0):
    lp_height = lp_frame.shape[0]

    # definding kernels for blurring
    blurred_lp = cv2.GaussianBlur(cv2.cvtColor(lp_frame, cv2.COLOR_BGR2GRAY), get_blur_kernel(lp_height), 0)

    binary_lp = cv2.threshold(src=blurred_lp, thresh=125, maxval=255, type=cv2.THRESH_OTSU)[1]

    dia_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, get_dia_kernel(lp_height))
    dia_img = cv2.morphologyEx(binary_lp, cv2.MORPH_DILATE, dia_kernel)

    cv2.imwrite('detected.jpg', dia_img)

    f, s, projs = proj_points(dia_img, ratio=5, verbose=0)
    if verbose : print(f, s)

    upper_portion = dia_img[f[0]:s[-1]]
    lower_portion = dia_img[s[-2]: lp_height-3]

    up_lettter = get_letter(upper_portion, dia_img)
    low_letter = get_letter(lower_portion, dia_img)
    print("Detect {} letters upper portion...".format(len(up_lettter)))
    print("Detect {} letters lower portion...".format(len(low_letter)))

    return (up_lettter, low_letter)


def get_letter(part, full):
    cont, _  = cv2.findContours(part, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    digit_w, digit_h = 30, 60
    copy_one = part.copy()
    crop_characters = []
    for c in sort_contours(cont):
        (x, y, w, h) = cv2.boundingRect(c)
        ratio = h/w
        if 1<=ratio<=3.5: # Only select contour with defined ratio
            if h/part.shape[0]>=0.5: # Select contour which has the height larger than 50% of the plate
                # Draw bounding box arroung digit number
                cv2.rectangle(copy_one, (x, y), (x + w, y + h), (0, 255,0), 2)

                # Sperate number and gibe prediction
                curr_num = full[y:y+h,x:x+w]
                curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
                _, curr_num = cv2.threshold(curr_num, 220, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                crop_characters.append(curr_num)
    return crop_characters