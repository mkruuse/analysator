import struct
import xml.etree.ElementTree as ET
import ast
import numpy as np
from reduction import datareducers,data_operators
from collections import Iterable


class VlsvWriter(object):
   ''' Class for reading VLSV files
   '''
   def __init__(self, vlsvReader, file_name ):
      ''' Initializes the vlsv file (opens the file, reads the file footer and reads in some parameters)

          :param vlsvReader:    Some open vlsv file for creating an XML footer as well as the grid
          :param file_name:     Name of the vlsv file where to input data
      '''
      self.__file_name = file_name
      self.__fptr = open(self.__file_name,"wb")

      self.__xml_root = ET.fromstring("<VLSV></VLSV>")
      self.__fileindex_for_cellid={}

      self.__offset = 0
      # Write endianness
      np.array(0, dtype=np.uint64).tofile(self.__fptr)
      # Write xml_offset, for now put this to zero:
      np.array(0, dtype=np.uint64).tofile(self.__fptr)

      self.__initialize()

      self.__fptr.close()

   def __initialize( self ):
      ''' Writes the xml footer as well as the cell ids from the vlsvReader to the file and everything else needed for the grid
      '''
      # Write parameters:
      data = vlsvReader.read_parameter("vxblocks_ini")
      self.write(data=data, name='vxblocks_ini', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("vyblocks_ini")
      self.write(data=data, name='vyblocks_ini', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("vzblocks_ini")
      self.write(data=data, name='vzblocks_ini', tag="PARAMETER", mesh='SpatialGrid')

      data = vlsvReader.read_parameter("xcells_ini")
      self.write(data=data, name='xcells_ini', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("ycells_ini")
      self.write(data=data, name='ycells_ini', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("zcells_ini")
      self.write(data=data, name='zcells_ini', tag="PARAMETER", mesh='SpatialGrid')

      data = vlsvReader.read_parameter("xmin")
      self.write(data=data, name='xmin', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("ymin")
      self.write(data=data, name='ymin', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("zmin")
      self.write(data=data, name='zmin', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("xmax")
      self.write(data=data, name='xmax', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("ymax")
      self.write(data=data, name='ymax', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("zmax")
      self.write(data=data, name='zmax', tag="PARAMETER", mesh='SpatialGrid')

      data = vlsvReader.read_parameter("vxmin")
      self.write(data=data, name='vxmin', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("vymin")
      self.write(data=data, name='vymin', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("vzmin")
      self.write(data=data, name='vzmin', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("vxmax")
      self.write(data=data, name='vxmax', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("vymax")
      self.write(data=data, name='vymax', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("vzmax")
      self.write(data=data, name='vzmax', tag="PARAMETER", mesh='SpatialGrid')

      data = vlsvReader.read_parameter("t")
      self.write(data=data, name='t', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("dt")
      self.write(data=data, name='dt', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("tstep")
      self.write(data=data, name='tstep', tag="PARAMETER", mesh='SpatialGrid')
      data = vlsvReader.read_parameter("fileIndex")
      self.write(data=data, name='fileIndex', tag="PARAMETER", mesh='SpatialGrid')


      # Write mesh bounding box:
      self.write(data=vlsvReader.read(name="", tag="MESH_BBOX", mesh="SpatialGrid"), name="", tag="MESH_BBOX", mesh="SpatialGrid")

      # Write nodes:
      self.write(data=vlsvReader.read(name="", tag="MESH_NODE_CRDS_X", mesh="SpatialGrid"), name="", tag="MESH_NODE_CRDS_X", mesh="SpatialGrid")

      # Write cell ids:
      self.write(data=vlsvReader.read(name="CellID", tag="VARIABLE", mesh="SpatialGrid"), name="CellID", tag="VARIABLE", mesh="SpatialGrid")

      # Some attributes for the MESH array that are mandatory to define:
      extra_attribs = {}
      extra_attribs['type'] = "multi_ucd"
      extra_attribs['xperiodic'] = 'yes'
      extra_attribs['yperiodic'] = 'yes'
      extra_attribs['zperiodic'] = 'yes'
      # Write zone global ids:
      self.write(data=vlsvReader.read(name="SpatialGrid", tag="MESH", mesh=""), name="SpatialGrid", tag="MESH", mesh="", extra_attribs=extra_attribs)

      # Write domain sizes
      self.write(data=vlsvReader.read( name='', tag='MESH_DOMAIN_SIZES', mesh="SpatialGrid" ), name='', tag='MESH_DOMAIN_SIZES', mesh="SpatialGrid" )

   def write(self, data, name, tag, mesh, extra_attribs=''):
      ''' Writes an array into the vlsv file

      :param name: Name of the data array
      :param tag:  Tag of the data array.
      :param mesh: Mesh for the data array
      :param extra_attribs: Dictionary with whatever xml attributes that should be defined in the array that aren't name, tag, or mesh

      :returns: True if the data was written successfully

      '''
      # Make sure the data is in numpy array format:
      data = np.array(data, copy=False)
      if self.__fptr.closed:
         fptr = open(self.__file_name,"wb")
      else:
         fptr = self.__fptr

      datatype = ''

      # Add the data into the xml data:
      child = ET.SubElement(parent=self.__xml_root, tag=tag)
      child.attrib["name"] = name
      child.attrib["mesh"] = mesh
      child.attrib["arraysize"] = len(np.atleast_1d(array))
      if extra_attribs != '':
         for i in extra_attribs.iteritems():
            child.attrib[i[0]] = i[1]
      if len(np.shape(array)) == 2:
         child.attrib["vectorsize"] = np.shape(array)[1]
         datatype = str(type(array[0][0]))
      elif len(np.shape(array)) > 2:
         print "ERROR, np.shape returned len(np.shape(array)) > 2"
         return False
      else:
         child.attrib["vectorsize"] = 1
         datatype = str(type(array[0]))

      # Parse the data types:
      if 'uint' in datatype:
         child.attrib["datatype"] = "uint"
      elif 'int' in datatype:
         child.attrib["datatype"] = "int"
      elif 'float' in datatype:
         child.attrib["datatype"] = "float"
      else:
         print "BAD DATATYPE"
         return False

      if '64' in datatype:
         child.attrib["datasize"] = 8
      elif '32' in datatype:
         child.attrib["datasize"] = 4
      else:
         print "BAD DATASIZE"
         return False

      data.tofile(fptr)
      current_offset = fptr.tell()

      # Info the xml about the file offset:
      child.text = str(current_offset)

      if self.__fptr.closed:
         fptr.close()

   def __write_xml_footer( self ):
      # Write the xml footer:
      current_offset = fptr.tell()
      max_xml_size = 1000000
      if self.__fptr.closed:
         fptr = open(self.__file_name,"wb")
      else:
         fptr = self.__fptr
      self.__xml_root.write( fptr )
      # Write the offset (first 8 bytes = endianness):
      offset_endianness = 8
      fptr.seek( offset_endianness )
      # Write the offset:
      np.array(current_offset, ndtype=np.uint64).tofile(fptr)
      # Go back to the previous offset:
      fptr.seek(current_offset)
      if self.__fptr.closed:
         fptr.close()

   def close():
      self.__write_xml_footer()
      self.__fptr.close()


