import math, copy, sys
# Length in mm considered to be 0 and its square

veryShort = 0.001
veryShort2 = veryShort*veryShort

# Roughly the largest dimension in mm of anything that will be dealt with

veryLong = 7000

class Point2D:
 def __init__(self, x = 0, y = 0, f = None):
  self.x = x
  self.y = y
  self.face = f

 def __repr__(self):
  return "<Point2D x:%s y:%s>" % (self.x, self.y)

 def Print(self):
  print(self.x, ',' , self.y)

 # Vector addition and subtraction

 def Add(self, p):
  result = copy.deepcopy(self)
  result.x = result.x + p.x
  result.y = result.y + p.y
  return result

 def Sub(self, p):
  result = copy.deepcopy(self)
  result.x = result.x - p.x
  result.y = result.y - p.y
  return result

 # Squared magnitude

 def Length2(self):
  return self.x*self.x + self.y*self.y

 # Multiplication by a scalar

 def Multiply(self, m):
  result = copy.deepcopy(self)
  result.x = result.x*m
  result.y = result.y*m
  return result  

 # Inner product

 def Dot(self, p):
  return self.x*p.x + self.y*p.y

 # Outer product

 def Cross(self, p):
  return self.x*p.y - self.y*p.x

# Set or change the associated face

 def SetFace(self, f):
  self.face = f
  
  # Small class for working with 2D parametric lines
# --------------------------------------------------------------


# Lines are defined by a start and end point.  The parameterisation
# is such that the start point has parameter = 0, and the end parameter = 1.

class Line2D:
 def __init__(self, p0 = Point2D(0, 0), p1 = Point2D(0, 0), f = None):
  self.p0 = p0
  self.direction = p1.Sub(p0)
  self.face = f
  self.empty = self.Length2() < veryShort2

 def __repr__(self):
  return "<Line2D p0:%s direction:%s>" % (self.p0, self.direction)

# The point at parameter value t

 def Point(self, t):
  p = self.direction.Multiply(t)
  return self.p0.Add(p)

 # Fine the parameter value at which another line crosses me (s) and I cross it (t)

 def Cross(self, otherLine):
  determinant = otherLine.direction.Cross(self.direction)
  if abs(determinant) < veryShort2:
   return None, None # Lines parallel
  dp = otherLine.p0.Sub(self.p0)
  s = otherLine.direction.Cross(dp)/determinant
  t = self.direction.Cross(dp)/determinant
  return s, t

 # Are two lines the same (within tolerance)?

 def IsSameLine(self, otherLine):
  determinant = otherLine.direction.Cross(self.direction)
  if abs(determinant) > veryShort2:
   return False
  if self.p0.Sub(otherLine.p0).Length2() > veryShort2:
   return False
  return True

 # Squared length

 def Length2(self):
  return self.direction.Length2()
