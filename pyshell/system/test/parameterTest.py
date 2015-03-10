#!/usr/bin/python
# -*- coding: utf-8 -*-

#Copyright (C) 2015  Jonathan Delvaux <pyshell@djoproject.net>

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

import unittest
from pyshell.system.parameter import Parameter

class ParameterTest(unittest.TestCase):
    def setUp(self):
        pass

    ## misc ##
    
    def test_ParameterMisc1(self):#test synchronized, simple execution test without other thread
        pass #TODO
        
    def test_ParameterMisc2(self):#isAValidStringPath, with invalid string
        pass #TODO
    
    def test_ParameterMisc3(self):#isAValidStringPath with empty string
        pass #TODO
        
    def test_ParameterMisc4(self):#isAValidStringPath with no char between two point
        pass #TODO
        
    def test_ParameterMisc5(self):#isAValidStringPath with no point in string 
        pass #TODO
        
    def test_ParameterMisc6(self):#isAValidStringPath with point in string
        pass #TODO
        
    ## ParameterManager constructor ##
    
    def test_ParameterManagerConstructor1(self):#with parent None + test getCurrentId
        pass #TODO
        
    def test_ParameterManagerConstructor2(self):#with valid parent + test getCurrentId
        pass #TODO
        
    def test_ParameterManagerConstructor3(self):#with parent without getCurrentId + test getCurrentId
        pass #TODO
    
    ## ParameterManager methods ##
    
    def test_ParameterManager1(self):#_buildExistingPathFromError, with 0 token found and some wrong token
        pass #TODO
    
    def test_ParameterManager2(self):#_buildExistingPathFromError, with some token found and 0 wrong token
        pass #TODO
    
    def test_ParameterManager3(self):#_buildExistingPathFromError, with some token found and some wrong token
        pass #TODO
    
    
    def test_ParameterManager4(self):#_getAdvanceResult, search a invalid path
        pass #TODO
    
    def test_ParameterManager5(self):#_getAdvanceResult, raiseIfAmbiguous=True and ambiguous
        pass #TODO
    
    def test_ParameterManager6(self):#_getAdvanceResult, raiseIfAmbiguous=True and not ambiguous
        pass #TODO
    
    def test_ParameterManager7(self):#_getAdvanceResult, raiseIfAmbiguous=False and ambiguous
        pass #TODO
    
    
    def test_ParameterManager8(self):#_getAdvanceResult, raiseIfNotFound=True and not found
        pass #TODO
    
    def test_ParameterManager9(self):#_getAdvanceResult, raiseIfNotFound=True and found
        pass #TODO
    
    def test_ParameterManager10(self):#_getAdvanceResult, raiseIfNotFound=False and not found
        pass #TODO
    
    def test_ParameterManager11(self):#_getAdvanceResult, with or withou perfectMatch
        pass #TODO
    
    
    def test_ParameterManager12(self):#test getAllowedType
        pass #TODO
    
    def test_ParameterManager13(self):#test isAnAllowedType, should not allow inherited type
        pass #TODO
    
    def test_ParameterManager14(self):#test extractParameter, with a valid type
        pass #TODO
    
    def test_ParameterManager15(self):#test extractParameter, with another parameter type
        pass #TODO
    
    def test_ParameterManager16(self):#test extractParameter, with something else (to try to instanciate an allowed type)
        pass #TODO
    
    
    def test_ParameterManager17(self):#setParameter, local exists + local + existing is readonly
        pass #TODO
    
    def test_ParameterManager18(self):#setParameter, local exists + local + existing is removable
        pass #TODO
    
    def test_ParameterManager19(self):#setParameter, global exists (not local) + local + existing is readonly
        pass #TODO
    
    def test_ParameterManager20(self):#setParameter, global exists (not local) + local + existing is removable
        pass #TODO
    
    def test_ParameterManager21(self):#setParameter, nothing exists + local
        pass #TODO
    
    
    def test_ParameterManager22(self):#setParameter, local exists + global + existing is readonly
        pass #TODO
    
    def test_ParameterManager23(self):#setParameter, local exists + global + existing is removable
        pass #TODO
    
    def test_ParameterManager24(self):#setParameter, global exists (not local) + global + existing is readonly
        pass #TODO
    
    def test_ParameterManager25(self):#setParameter, global exists (not local) + global + existing is removable
        pass #TODO
    
    def test_ParameterManager26(self):#setParameter, nothing exists + global
        pass #TODO
    
    
    def test_ParameterManager27(self):#getParameter, local exists + localParam=True + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager28(self):#getParameter, local exists + localParam=True + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager29(self):#getParameter, global exists + localParam=True + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager30(self):#getParameter, global exists + localParam=True + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager31(self):#getParameter, local exists + localParam=False + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager32(self):#getParameter, local exists + localParam=False + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager33(self):#getParameter, global exists + localParam=False + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager34(self):#getParameter, global exists + localParam=False + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager35(self):#getParameter, nothing exists + localParam=True + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager36(self):#getParameter, nothing exists + localParam=True + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager37(self):#getParameter, nothing exists + localParam=False + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager38(self):#getParameter, nothing exists + localParam=False + exploreOtherLevel=False
        pass #TODO
    
    
    def test_ParameterManager39(self):#hasParameter, local exists + localParam=True + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager40(self):#hasParameter, local exists + localParam=True + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager41(self):#hasParameter, global exists + localParam=True + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager42(self):#hasParameter, global exists + localParam=True + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager43(self):#hasParameter, local exists + localParam=False + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager44(self):#hasParameter, local exists + localParam=False + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager45(self):#hasParameter, global exists + localParam=False + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager46(self):#hasParameter, global exists + localParam=False + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager47(self):#hasParameter, nothing exists + localParam=True + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager48(self):#hasParameter, nothing exists + localParam=True + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager49(self):#hasParameter, nothing exists + localParam=False + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager50(self):#hasParameter, nothing exists + localParam=False + exploreOtherLevel=False
        pass #TODO
    
    
    def test_ParameterManager51(self):#unsetParameter, local exists + localParam=True + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager52(self):#unsetParameter, local exists + localParam=True + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager53(self):#unsetParameter, global exists + localParam=True + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager54(self):#unsetParameter, global exists + localParam=True + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager55(self):#unsetParameter, local exists + localParam=False + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager56(self):#unsetParameter, local exists + localParam=False + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager57(self):#unsetParameter, global exists + localParam=False + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager58(self):#unsetParameter, global exists + localParam=False + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager59(self):#unsetParameter, local + global exists + localParam=False + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager60(self):#unsetParameter, local + global exists + localParam=False + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager61(self):#unsetParameter, global + local exists + localParam=True + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager62(self):#unsetParameter, global + local exists + localParam=True + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager63(self):#unsetParameter, nothing exists + localParam=True + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager64(self):#unsetParameter, nothing exists + localParam=True + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager65(self):#unsetParameter, nothing exists + localParam=False + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager66(self):#unsetParameter, nothing exists + localParam=False + exploreOtherLevel=False
        pass #TODO
    
    
    def test_ParameterManager67(self):#flushVariableLevelForThisThread, nothing for the current thread
        pass #TODO
    
    def test_ParameterManager68(self):#flushVariableLevelForThisThread, flush parameter that only exists for the current thread
        pass #TODO
    
    def test_ParameterManager69(self):#flushVariableLevelForThisThread, flush parameter that exist for the current thread and at global level
        pass #TODO
    
    def test_ParameterManager70(self):#flushVariableLevelForThisThread, flush parameter that exist for the current thread and for others thread
        pass #TODO
    
    
    def test_ParameterManager71(self):#buildDictionnary, search with invalid string
        pass #TODO
    
    def test_ParameterManager72(self):#buildDictionnary, local exists + localParam=True + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager73(self):#buildDictionnary, local exists + localParam=True + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager74(self):#buildDictionnary, global exists + localParam=True + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager75(self):#buildDictionnary, global exists + localParam=True + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager76(self):#buildDictionnary, local exists + localParam=False + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager77(self):#buildDictionnary, local exists + localParam=False + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager78(self):#buildDictionnary, global exists + localParam=False + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager79(self):#buildDictionnary, global exists + localParam=False + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager80(self):#buildDictionnary, nothing exists + localParam=True + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager81(self):#buildDictionnary, nothing exists + localParam=True + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager82(self):#buildDictionnary, nothing exists + localParam=False + exploreOtherLevel=True
        pass #TODO
    
    def test_ParameterManager83(self):#buildDictionnary, nothing exists + localParam=False + exploreOtherLevel=False
        pass #TODO
    
    def test_ParameterManager84(self):#unsetParameter, local + global exists + localParam=False + exploreOtherLevel=True  (mixe several cases)
        pass #TODO
    
    def test_ParameterManager85(self):#unsetParameter, local + global exists + localParam=False + exploreOtherLevel=False (mixe several cases)
        pass #TODO
    
    def test_ParameterManager86(self):#unsetParameter, global + local exists + localParam=True + exploreOtherLevel=True   (mixe several cases)
        pass #TODO
    
    def test_ParameterManager87(self):#unsetParameter, global + local exists + localParam=True + exploreOtherLevel=False  (mixe several cases)
        pass #TODO
    
        
    ## parameters test ##
    def test_Parameter1(self):#test transient with the constructor
        pass #TODO
    
    def test_Parameter2(self):#test getValue (will return None)
        pass #TODO
    
    def test_Parameter3(self):#test setValue (won't do anything)
        pass #TODO
    
    def test_Parameter4(self):#test setTransient + isTransient
        pass #TODO
    
    def test_Parameter5(self):#test isReadOnly
        pass #TODO
    
    def test_Parameter6(self):#test isRemovable
        pass #TODO
    
    def test_Parameter7(self):#test str
        pass #TODO
    
    def test_Parameter8(self):#test repr
        pass #TODO
    
    def test_Parameter9(self):#test getProperties
        pass #TODO
    
        
if __name__ == '__main__':
    unittest.main()
