"""Functions for creating files needed for other software"""

import numpy as np
import os
from atom import Atom
from random import randint

# edits a cp2k template file called cp2k.template.in
# and writes a new version called cp2k.[input name].in
# with required lattice vectors and atomic positions


def write_cp2k(in_name, file_name, vectors, atoms, temp_name):
    """
    Make a cp2k input file from a template.

    To use this, first make a template file with the name as XXX__NAME__XXX,
    the vectors as XXX__AVEC__XXX, XXX__BVEC__XXX and XXX__CVEC__XXX and the
    positions as XXX__POS__XXX.

    Parameters
    ----------
    in_name : string
        Project name
    file_name : string
        Name of the cp2k input file
    vectors : 3x3 matrix
        Lattice vectors
    atoms : list of Atom objects
        Atoms in the system
    temp_name : string
        Name of the template file


    """
    with open(temp_name) as temp_file:
        temp_content = temp_file.readlines()

    # strings for each lattice vector
    aVec = "{:10.6f} {:10.6f} {:10.6f}".format(*vectors[0])
    bVec = "{:10.6f} {:10.6f} {:10.6f}".format(*vectors[1])
    cVec = "{:10.6f} {:10.6f} {:10.6f}".format(*vectors[2])

    cp2k_in = open(file_name, "w")

    for line in temp_content:

        # writes the name of the calculation at the top of the file
        if "XXX__NAME__XXX" in line:
            cp2k_in.write(line.replace("XXX__NAME__XXX", in_name))

        # replace the tags with the coordinates of lattice vectors
        elif "XXX__AVEC__XXX" in line:
            cp2k_in.write(line.replace("XXX__AVEC__XXX", aVec))
        elif "XXX__BVEC__XXX" in line:
            cp2k_in.write(line.replace("XXX__BVEC__XXX", bVec))
        elif "XXX__CVEC__XXX" in line:
            cp2k_in.write(line.replace("XXX__CVEC__XXX", cVec))

        # writes atomic coordinates
        elif "XXX__POS__XXX" in line:
            for atom in atoms:
                line_str = "{:>6} {:10.6f} {:10.6f} {:10.6f}".format(
                    atom.elem, atom.x, atom.y, atom.z)
                cp2k_in.write(line_str + "\n")

        else:  # if no tag is found
            cp2k_in.write(line)

    cp2k_in.close()
    return


def write_xyz(in_name, atoms):
    """
    Write an xyz file.

    Parameters
    ----------
    in_name : string
        Name of the xyz file. Include the file extension, e.g. "molecule.xyz"
    atoms : list of Atom objects
        Atms to write
    """
    outFile = open(in_name, "w")
    outFile.write(str(len(atoms)) + "\n")
    outFile.write(in_name + "\n")

    for atom in atoms:
        outFile.write(atom.xyz_str() + "\n")
    outFile.close()
    return


def write_uc(in_name, vectors, aN, bN, cN, atoms):
    """
    Write a .uc file for Ewald.c.

    .uc files are written in fractional coordinates instead of Cartesian

    Parameters
    ----------
    in_name : string
        Name of the file to be written
    vectors : 3x3 matrix
        Lattice vectors
    aN,bN,cN : ints
        Number of times each lattice vector should be multiplied
    atoms : list of Atom objects
        Unit cell atoms for the file

    """
    line1 = vectors[0].tolist() + [aN]
    line2 = vectors[1].tolist() + [bN]
    line3 = vectors[2].tolist() + [cN]
    outFile = open(in_name, "w")
    outFile.write("{:10.6f} {:10.6f} {:10.6f} {:10d}".format(*line1) + "\n")
    outFile.write("{:10.6f} {:10.6f} {:10.6f} {:10d}".format(*line2) + "\n")
    outFile.write("{:10.6f} {:10.6f} {:10.6f} {:10d}".format(*line3) + "\n")

    # transpose to get the transformation matrix
    M = np.transpose(vectors)
    # inverse transformation matrix
    U = np.linalg.inv(M)

    for atom in atoms:
        # change of basis transformation
        dir_pos = [atom.x, atom.y, atom.z]
        frac_pos = np.dot(U, dir_pos).tolist()
        for coord in frac_pos:
            # if the coordinate is negative
            if coord < 0:
                # translate it to the range [0,1]
                frac_pos[frac_pos.index(coord)] = 1 + coord
        str_line = "{:10.6f} {:10.6f} {:10.6f} {:10.6f} {:>6}".format(
            *frac_pos + [atom.q] + [atom.elem]) + "\n"
        outFile.write(str_line)
    outFile.close()
    return


def write_qc(in_name, atoms):
    "Write a .qc file for Ewald.c."
    outFile = open(in_name, "w")
    for atom in atoms:
        str_line = "{:>6} {:10.6f} {:10.6f} {:10.6f} {:10.6f}".format(
            atom.elem, atom.x, atom.y, atom.z, atom.q) + "\n"
        outFile.write(str_line)
    outFile.close()
    return


def write_ew_in(in_name, file_name, nChk, nAt):
    """
    Write an input file for Ewald.c.

    Remember to include and pre or post fixes to the file name. Following the
    convention from the paper, it would be something like "in.ewald.somename"

    Parameters
    ----------
    in_name : string
        Name of the project
    file_name : string
        Name of the input file to write
    nChk : int
        Number of random checkpoints in zone 1
    nAt : int
        Number of fixed charge atoms in zone 1+2

    """
    outFile = open((file_name), "w")
    outFile.write(in_name + "\n")
    outFile.write(str(nChk) + "\n")
    outFile.write(str(nAt) + "\n")
    outFile.write("0\n")
    outFile.close()
    return


def write_seed():
    """Write a seedfile for Ewald.c"""
    outFile = open("seedfile", "w")
    seed1 = randint(1, 2**31 - 86)
    seed2 = randint(1, 2**31 - 250)
    outFile.write(str(seed1) + " " + str(seed2))
    outFile.close()

def write_gauss(in_name, file_name, atoms, points, temp_name):
    """
    Write a Gaussian input file.

    A template file needs to be prepared which has the name as XXX__NAME__XXX,
    the positions as XXX__POS__XXX and the (optional) charges as
    XXX__CHARGES__XXX.

    Parameters
    ----------
    in_name : str
        Project name
    file_name : str
        Name of the Gaussian input file to be written
    atoms : list of Atom objects
        Atoms to be calculated with Gaussian
    points : list of Atom objects or None
        The Atom objects should have a charge. If there is no XXX__CHARGES__XXX
        in the template file, this doesn't matter and can be None
    temp_name : str
        Name of the template file

    """
    with open(temp_name) as temp_file:
        temp_content = temp_file.readlines()

    outFile = open(file_name, "w")

    for line in temp_content:
        if "XXX__NAME__XXX" in line:
            outFile.write(line.replace("XXX__NAME__XXX", in_name))
        elif "XXX__POS__XXX" in line:
            for atom in atoms:
                atomStr = "{:>6} {:10.6f} {:10.6f} {:10.6f}".format(
                    atom.elem, atom.x, atom.y, atom.z) + "\n"
                outFile.write(atomStr)
        elif "XXX__CHARGES__XXX" in line:
            for point in points:
                point_str = "{:10.6f} {:10.6f} {:10.6f} {:10.6f}".format(
                    point.x, point.y, point.z, point.q) + "\n"
                outFile.write(point_str)
        else:
            outFile.write(line)
    outFile.close()
    return

def write_g_temp(in_name, file_name, fixed_atoms, points, temp_name):
    """
    Write a Gaussian input template file.

    This serves to generate templates for write_gauss. That's right, you are
    going to need to make templates for your templates files so that you can
    generate inputs while you generate inputs. In this case a XXX__POS__XXX tag
    should be included and won't be overwritten.

    Parameters
    ----------
    in_name : str
        Project name
    file_name : str
        Name of the Gaussian input file to be written
    fixed_atoms : list of Atom objects
        Atoms to be calculated with Gaussian with the -1 tag which makes them
        fixed in space
    points : list of Atom objects or None
        The Atom objects should have a charge. If there is no XXX__CHARGES__XXX
        in the template file, this doesn't matter and can be None
    temp_name : str
        Name of the template file

    """
    with open(temp_name) as temp_file:
        temp_content = temp_file.readlines()

    outFile = open(file_name, "w")

    for line in temp_content:
        if "XXX__NAME__XXX" in line:
            outFile.write(line.replace("XXX__NAME__XXX", in_name))
        elif "XXX__FIX__XXX" in line:
            for atom in fixed_atoms:
                atomStr = "{:>6} -1 {:10.6f} {:10.6f} {:10.6f}".format(
                    atom.elem, atom.x, atom.y, atom.z) + "\n"
                outFile.write(atomStr)
        elif "XXX__CHARGES__XXX" in line:
            for point in points:
                point_str = "{:10.6f} {:10.6f} {:10.6f} {:10.6f}".format(
                    point.x, point.y, point.z, point.q) + "\n"
                outFile.write(point_str)
        else:
            outFile.write(line)
    outFile.close()
    return

def edit_vasp_pos(in_name, atoms):
    """
    Overwrite vasp POSCAR file.

    Parameters
    ----------
    in_name : str
        Name of the VASP file
    atoms : list of Atom objects
        Atoms to be written in the POSCAR file

    """
    with open(in_name + ".vasp") as vaspFile:
        content = vaspFile.readlines()

    outFile = open(in_name + ".new.vasp", "w")

    for line in content:
        outFile.write(line)
        if "Cartesian" in line:
            break
    for atom in atoms:
        atomStr = "{:10.6f} {:10.6f} {:10.6f}".format(
            atom.x, atom.y, atom.z) + "\n"
        outFile.write(atomStr)
    return


def write_qe(in_name, file_name, vectors, atoms, temp_name):
    """
    Write a Quantum Espresso (QE) input file.

    Parameters
    ----------
    in_name : str
        Project name
    file_name : str
        Name of the QE input file
    vectors : 3x3 matrix
        Lattice vectors
    atoms : list of Atom objects
        Atoms to be calculated with QE
    temp_name : str
        Name of the template file

    """
    with open(temp_name) as temp_file:
        temp_content = temp_file.readlines()

    # strings for each lattice vector
    aVec = "{:10.6f} {:10.6f} {:10.6f}".format(*vectors[0])
    bVec = "{:10.6f} {:10.6f} {:10.6f}".format(*vectors[1])
    cVec = "{:10.6f} {:10.6f} {:10.6f}".format(*vectors[2])

    qe_in = open(file_name, "w")

    for line in temp_content:

        # writes the name of the calculation at the top of the file
        if "XXX__NAME__XXX" in line:
            qe_in.write(line.replace("XXX__NAME__XXX", in_name))

        # replace the tags with the coordinates of lattice vectors
        elif "XXX__AVEC__XXX" in line:
            qe_in.write(line.replace("XXX__AVEC__XXX", aVec))
        elif "XXX__BVEC__XXX" in line:
            qe_in.write(line.replace("XXX__BVEC__XXX", bVec))
        elif "XXX__CVEC__XXX" in line:
            qe_in.write(line.replace("XXX__CVEC__XXX", cVec))

        # writes atomic coordinates
        elif "XXX__POS__XXX" in line:
            for atom in atoms:
                line_str = "{:<6} {:10.6f} {:10.6f} {:10.6f}".format(
                    atom.elem, atom.x, atom.y, atom.z)
                qe_in.write(line_str + "\n")

        else:  # if no tag is found
            qe_in.write(line)
    qe_in.close()
    return


def write_pp(in_name, file_name, temp_name):
    """
    Write a Quantum Espresso .pp file

    This is a file for PP.x calculations which generate things like cube files

    Parameters
    ----------
    in_name : str
        Project name
    file_name : str
        Name of the .pp file. Include the extension e.g. "example.pp"
    temp_name :
        Name of the template file

    """
    with open(temp_name) as temp_file:
        temp_content = temp_file.readlines()

    pp_in = open(file_name, "w")

    for line in temp_content:

        if "XXX__NAME__XXX" in line:
            pp_in.write(line.replace("XXX__NAME__XXX", in_name))
        else:
            pp_in.write(line)
    pp_in.close()
    return
