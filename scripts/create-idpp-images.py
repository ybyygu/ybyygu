#! /usr/bin/env python
# idpp-images.py

# [[file:~/Workspace/Programming/chem-utils/chem-utils.note::*idpp-images.py][idpp-images.py:1]]
import numpy as np
import ase.io
from ase.neb import NEB

def show_image_distances(images):
    print("distances...")

    nimages = len(images)
    # print image distances
    for i in range(nimages-1):
        positions_this = images[i].positions
        positions_next = images[i+1].positions
        distance = np.linalg.norm(positions_next - positions_this)
        print("image distance {:02} between {:02} = {:-6.3f}".format(i, i+1, distance))

def create_idpp_images(initial, final, nimages):
    """create IDPP images, which will apply NEB minimization to make images even
    distributed
    """
    # create nimages
    images = [initial]
    images += [initial.copy() for i in range(nimages-2)]
    images += [final]
    neb = NEB(images, remove_rotation_and_translation=True, method="improvedtangent")

    # run linear or IDPP interpolation
    neb.interpolate("idpp")

    show_image_similarity(images)
    show_image_distances(images)

    return images

def create_lst_images(freactant, fproduct, nimages, mic=False):
    """create simplified LST images without NEB minimization

    Parameters
    ----------
    freactant: path to initial atoms
    fproduct : path to final atoms
    nimages: the number of images to be interpolated including two endpoints
    mic    : apply mic or not (PBC)
    """
    from ase.neb import IDPP
    from ase.optimize import BFGS
    from ase.build import minimize_rotation_and_translation

    initial = ase.io.read(freactant)
    final   = ase.io.read(fproduct)
    images = [initial]
    images += [initial.copy() for i in range(nimages-2)]
    images += [final]

    nimages = len(images)
    d1 = images[0].get_all_distances(mic=mic)
    d2 = images[-1].get_all_distances(mic=mic)
    d = (d2 - d1) / (nimages - 1)
    for i, image in enumerate(images):
        image.set_calculator(IDPP(d1 + i * d, mic=mic))
        qn = BFGS(image)
        qn.run(fmax=0.1)
    # apply optimal translation and rotation
    for i in range(nimages-1):
        minimize_rotation_and_translation(images[i], images[i+1])

    show_image_similarity(images)
    show_image_distances(images)

    return images

def show_idpp_energies_and_forces(fimages, mic=False, opt=False):
    """evaluate images using IDPP scheme

    Parameters
    ----------
    fimages: the path to images file
    mic    : apply mic or not (PBC)
    opt    : opt images or not using IDPP scheme
    """
    from ase.neb import IDPP
    from ase.optimize import BFGS

    images = ase.io.read(fimages, index=":")

    nimages = len(images)
    d1 = images[0].get_all_distances(mic=mic)
    d2 = images[-1].get_all_distances(mic=mic)
    d = (d2 - d1) / (nimages - 1)
    old = []
    for i, image in enumerate(images):
        old.append(image.calc)
        image.calc = IDPP(d1 + i * d, mic=mic)
        energy = image.get_total_energy()
        forces = image.get_forces()
        print("image {:02} cost = {:-6.3f}".format(i, energy))
        if opt:
            qn = BFGS(image)
            qn.run(fmax=0.1)
    return images

def get_similarity(images):
    """Return the cosine similarities of intermediate images"""
    nimages = len(images)

    # collect transition vectors
    disp_vectors = []
    for i in range(nimages - 1):
        position_this = images[i].positions
        position_next = images[i+1].positions
        disp_vectors.append(position_next - position_this)

    # calculate cosin similarity between two neighboring vectors
    similarities = []
    for i in range(nimages-2):
        vthis = disp_vectors[i]
        vnext = disp_vectors[i+1]

        similarity = np.vdot(vnext, vthis) / np.linalg.norm(vnext) / np.linalg.norm(vthis)
        similarities.append(similarity)

    return similarities

def show_image_similarity(images):
    print("similarity...")

    similarities = get_similarity(images)
    for i, s in enumerate(similarities):
        print("image {:02} between {:02} similarity = {:-6.3f}".format(i, i+1, s))


if __name__ == '__main__':
    import sys
    initial = ase.io.read(sys.argv[1])
    final = ase.io.read(sys.argv[2])
    nimages = int(sys.argv[3])
    images = create_idpp_images(initial, final, nimages)
    ase.io.write("idpp.pdb", images)

    show_image_distances(images)
# idpp-images.py:1 ends here
