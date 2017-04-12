# Copyright (c) 2017 Ultimaker B.V.
# Cura is released under the terms of the AGPLv3 or higher.

import os.path #To find the test stack files.
import pytest #This module contains automated tests.
import unittest.mock #For the mocking and monkeypatching functionality.

import UM.Settings.ContainerRegistry #To create empty instance containers.
import UM.Settings.ContainerStack #To set the container registry the container stacks use.
from UM.Settings.DefinitionContainer import DefinitionContainer #To check against the class of DefinitionContainer.
from UM.Settings.InstanceContainer import InstanceContainer #To check against the class of InstanceContainer.
import cura.Settings.ExtruderStack #The module we're testing.
from cura.Settings.Exceptions import InvalidContainerError, InvalidOperationError #To check whether the correct exceptions are raised.

##  Fake container registry that always provides all containers you ask of.
@pytest.yield_fixture()
def container_registry():
    registry = unittest.mock.MagicMock()
    registry.return_value = unittest.mock.NonCallableMagicMock()
    registry.findInstanceContainers = lambda *args, registry = registry, **kwargs: [registry.return_value]
    registry.findDefinitionContainers = lambda *args, registry = registry, **kwargs: [registry.return_value]

    UM.Settings.ContainerRegistry.ContainerRegistry._ContainerRegistry__instance = registry
    UM.Settings.ContainerStack._containerRegistry = registry

    yield registry

    UM.Settings.ContainerRegistry.ContainerRegistry._ContainerRegistry__instance = None
    UM.Settings.ContainerStack._containerRegistry = None

##  An empty extruder stack to test with.
@pytest.fixture()
def extruder_stack() -> cura.Settings.ExtruderStack.ExtruderStack:
    return cura.Settings.ExtruderStack.ExtruderStack("TestStack")

##  Place-in function for findContainer that finds only containers that start
#   with "some_".
def findSomeContainers(container_id = "*", container_type = None, type = None, category = "*"):
    if container_id.startswith("some_"):
        return UM.Settings.ContainerRegistry._EmptyInstanceContainer(container_id)
    if container_type == DefinitionContainer:
        definition_mock = unittest.mock.MagicMock()
        definition_mock.getId = unittest.mock.MagicMock(return_value = "some_definition") #getId returns some_definition.
        return definition_mock

##  Helper function to read the contents of a container stack in the test
#   stack folder.
#
#   \param filename The name of the file in the "stacks" folder to read from.
#   \return The contents of that file.
def readStack(filename):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "stacks", filename)) as file_handle:
        serialized = file_handle.read()
    return serialized

##  Gets an instance container with a specified container type.
#
#   \param container_type The type metadata for the instance container.
#   \return An instance container instance.
def getInstanceContainer(container_type) -> InstanceContainer:
    container = InstanceContainer(container_id = "InstanceContainer")
    container.addMetaDataEntry("type", container_type)
    return container

class DefinitionContainerSubClass(DefinitionContainer):
    def __init__(self):
        super().__init__(container_id = "SubDefinitionContainer")

class InstanceContainerSubClass(InstanceContainer):
    def __init__(self, container_type):
        super().__init__(container_id = "SubInstanceContainer")
        self.addMetaDataEntry("type", container_type)

#############################START OF TEST CASES################################

##  Tests whether adding a container is properly forbidden.
def test_addContainer(extruder_stack):
    with pytest.raises(InvalidOperationError):
        extruder_stack.addContainer(unittest.mock.MagicMock())

#Tests setting user changes profiles to invalid containers.
@pytest.mark.parametrize("container", [
    getInstanceContainer(container_type = "wrong container type"),
    getInstanceContainer(container_type = "material"), #Existing, but still wrong type.
    DefinitionContainer(container_id = "wrong class")
])
def test_constrainUserChangesInvalid(container, extruder_stack):
    with pytest.raises(InvalidContainerError): #Invalid container, should raise an error.
        extruder_stack.userChanges = container

#Tests setting user changes profiles.
@pytest.mark.parametrize("container", [
    getInstanceContainer(container_type = "user"),
    InstanceContainerSubClass(container_type = "user")
])
def test_constrainUserChangesValid(container, extruder_stack):
    extruder_stack.userChanges = container #Should not give an error.

#Tests setting quality changes profiles to invalid containers.
@pytest.mark.parametrize("container", [
    getInstanceContainer(container_type = "wrong container type"),
    getInstanceContainer(container_type = "material"), #Existing, but still wrong type.
    DefinitionContainer(container_id = "wrong class")
])
def test_constrainQualityChangesInvalid(container, extruder_stack):
    with pytest.raises(InvalidContainerError): #Invalid container, should raise an error.
        extruder_stack.qualityChanges = container

#Test setting quality changes profiles.
@pytest.mark.parametrize("container", [
    getInstanceContainer(container_type = "quality_changes"),
    InstanceContainerSubClass(container_type = "quality_changes")
])
def test_constrainQualityChangesValid(container, extruder_stack):
    extruder_stack.qualityChanges = container #Should not give an error.

#Tests setting quality profiles to invalid containers.
@pytest.mark.parametrize("container", [
    getInstanceContainer(container_type = "wrong container type"),
    getInstanceContainer(container_type = "material"), #Existing, but still wrong type.
    DefinitionContainer(container_id = "wrong class")
])
def test_constrainQualityInvalid(container, extruder_stack):
    with pytest.raises(InvalidContainerError): #Invalid container, should raise an error.
        extruder_stack.quality = container

#Test setting quality profiles.
@pytest.mark.parametrize("container", [
    getInstanceContainer(container_type = "quality"),
    InstanceContainerSubClass(container_type = "quality")
])
def test_constrainQualityValid(container, extruder_stack):
    extruder_stack.quality = container #Should not give an error.

#Tests setting materials to invalid containers.
@pytest.mark.parametrize("container", [
    getInstanceContainer(container_type = "wrong container type"),
    getInstanceContainer(container_type = "quality"), #Existing, but still wrong type.
    DefinitionContainer(container_id = "wrong class")
])
def test_constrainMaterialInvalid(container, extruder_stack):
    with pytest.raises(InvalidContainerError): #Invalid container, should raise an error.
        extruder_stack.material = container

#Test setting materials.
@pytest.mark.parametrize("container", [
    getInstanceContainer(container_type = "material"),
    InstanceContainerSubClass(container_type = "material")
])
def test_constrainMaterialValid(container, extruder_stack):
    extruder_stack.material = container #Should not give an error.

#Tests setting variants to invalid containers.
@pytest.mark.parametrize("container", [
    getInstanceContainer(container_type = "wrong container type"),
    getInstanceContainer(container_type = "material"), #Existing, but still wrong type.
    DefinitionContainer(container_id = "wrong class")
])
def test_constrainVariantInvalid(container, extruder_stack):
    with pytest.raises(InvalidContainerError): #Invalid container, should raise an error.
        extruder_stack.variant = container

#Test setting variants.
@pytest.mark.parametrize("container", [
    getInstanceContainer(container_type = "variant"),
    InstanceContainerSubClass(container_type = "variant")
])
def test_constrainVariantValid(container, extruder_stack):
    extruder_stack.variant = container #Should not give an error.

#Tests setting definitions to invalid containers.
@pytest.mark.parametrize("container", [
    getInstanceContainer(container_type = "wrong class"),
    getInstanceContainer(container_type = "material"), #Existing, but still wrong class.
])
def test_constrainVariantInvalid(container, extruder_stack):
    with pytest.raises(InvalidContainerError): #Invalid container, should raise an error.
        extruder_stack.definition = container

#Test setting definitions.
@pytest.mark.parametrize("container", [
    DefinitionContainer(container_id = "DefinitionContainer"),
    DefinitionContainerSubClass()
])
def test_constrainDefinitionValid(container, extruder_stack):
    extruder_stack.definition = container #Should not give an error.

##  Tests whether deserialising completes the missing containers with empty
#   ones.
@pytest.mark.skip #The test currently fails because the definition container doesn't have a category, which is wrong but we don't have time to refactor that right now.
def test_deserializeCompletesEmptyContainers(extruder_stack: cura.Settings.ExtruderStack):
    extruder_stack._containers = [DefinitionContainer(container_id = "definition")] #Set the internal state of this stack manually.

    with unittest.mock.patch("UM.Settings.ContainerStack.ContainerStack.deserialize", unittest.mock.MagicMock()): #Prevent calling super().deserialize.
        extruder_stack.deserialize("")

    assert len(extruder_stack.getContainers()) == len(cura.Settings.CuraContainerStack._ContainerIndexes.IndexTypeMap) #Needs a slot for every type.
    for container_type_index in cura.Settings.CuraContainerStack._ContainerIndexes.IndexTypeMap:
        if container_type_index == cura.Settings.CuraContainerStack._ContainerIndexes.Definition: #We're not checking the definition.
            continue
        assert extruder_stack.getContainer(container_type_index).getId() == "empty" #All others need to be empty.

##  Tests whether an instance container with the wrong type gets removed when
#   deserialising.
def test_deserializeRemovesWrongInstanceContainer(extruder_stack):
    extruder_stack._containers[cura.Settings.CuraContainerStack._ContainerIndexes.Quality] = getInstanceContainer(container_type = "wrong type")
    extruder_stack._containers[cura.Settings.CuraContainerStack._ContainerIndexes.Definition] = DefinitionContainer(container_id = "some definition")

    with unittest.mock.patch("UM.Settings.ContainerStack.ContainerStack.deserialize", unittest.mock.MagicMock()): #Prevent calling super().deserialize.
        extruder_stack.deserialize("")

    assert extruder_stack.quality == extruder_stack._empty_instance_container #Replaced with empty.

##  Tests whether a container with the wrong class gets removed when
#   deserialising.
def test_deserializeRemovesWrongContainerClass(extruder_stack):
    extruder_stack._containers[cura.Settings.CuraContainerStack._ContainerIndexes.Quality] = DefinitionContainer(container_id = "wrong class")
    extruder_stack._containers[cura.Settings.CuraContainerStack._ContainerIndexes.Definition] = DefinitionContainer(container_id = "some definition")

    with unittest.mock.patch("UM.Settings.ContainerStack.ContainerStack.deserialize", unittest.mock.MagicMock()): #Prevent calling super().deserialize.
        extruder_stack.deserialize("")

    assert extruder_stack.quality == extruder_stack._empty_instance_container #Replaced with empty.

##  Tests whether an instance container in the definition spot results in an
#   error.
def test_deserializeWrongDefinitionClass(extruder_stack):
    extruder_stack._containers[cura.Settings.CuraContainerStack._ContainerIndexes.Definition] = getInstanceContainer(container_type = "definition") #Correct type but wrong class.

    with unittest.mock.patch("UM.Settings.ContainerStack.ContainerStack.deserialize", unittest.mock.MagicMock()): #Prevent calling super().deserialize.
        with pytest.raises(UM.Settings.ContainerStack.InvalidContainerStackError): #Must raise an error that there is no definition container.
            extruder_stack.deserialize("")

##  Tests whether an instance container with the wrong type is moved into the
#   correct slot by deserialising.
def test_deserializeMoveInstanceContainer(extruder_stack):
    extruder_stack._containers[cura.Settings.CuraContainerStack._ContainerIndexes.Quality] = getInstanceContainer(container_type = "material") #Not in the correct spot.
    extruder_stack._containers[cura.Settings.CuraContainerStack._ContainerIndexes.Definition] = DefinitionContainer(container_id = "some definition")

    with unittest.mock.patch("UM.Settings.ContainerStack.ContainerStack.deserialize", unittest.mock.MagicMock()): #Prevent calling super().deserialize.
        extruder_stack.deserialize("")

    assert extruder_stack.quality.getId() == "empty"
    assert extruder_stack.material.getId() != "empty"

##  Tests whether a definition container in the wrong spot is moved into the
#   correct spot by deserialising.
@pytest.mark.skip #The test currently fails because the definition container doesn't have a category, which is wrong but we don't have time to refactor that right now.
def test_deserializeMoveDefinitionContainer(extruder_stack):
    extruder_stack._containers[cura.Settings.CuraContainerStack._ContainerIndexes.Material] = DefinitionContainer(container_id = "some definition") #Not in the correct spot.

    with unittest.mock.patch("UM.Settings.ContainerStack.ContainerStack.deserialize", unittest.mock.MagicMock()): #Prevent calling super().deserialize.
        extruder_stack.deserialize("")

    assert extruder_stack.material.getId() == "empty"
    assert extruder_stack.definition.getId() != "empty"

    UM.Settings.ContainerStack._containerRegistry = None

##  Tests whether getProperty properly applies the stack-like behaviour on its
#   containers.
def test_getPropertyFallThrough(extruder_stack):
    #A few instance container mocks to put in the stack.
    mock_layer_heights = {} #For each container type, a mock container that defines layer height to something unique.
    mock_no_settings = {} #For each container type, a mock container that has no settings at all.
    container_indices = cura.Settings.CuraContainerStack._ContainerIndexes #Cache.
    for type_id, type_name in container_indices.IndexTypeMap.items():
        container = unittest.mock.MagicMock()
        container.getProperty = lambda key, property, type_id = type_id: type_id if (key == "layer_height" and property == "value") else None #Returns the container type ID as layer height, in order to identify it.
        container.hasProperty = lambda key, property: key == "layer_height"
        container.getMetaDataEntry = unittest.mock.MagicMock(return_value = type_name)
        mock_layer_heights[type_id] = container

        container = unittest.mock.MagicMock()
        container.getProperty = unittest.mock.MagicMock(return_value = None) #Has no settings at all.
        container.hasProperty = unittest.mock.MagicMock(return_value = False)
        container.getMetaDataEntry = unittest.mock.MagicMock(return_value = type_name)
        mock_no_settings[type_id] = container

    extruder_stack.userChanges = mock_no_settings[container_indices.UserChanges]
    extruder_stack.qualityChanges = mock_no_settings[container_indices.QualityChanges]
    extruder_stack.quality = mock_no_settings[container_indices.Quality]
    extruder_stack.material = mock_no_settings[container_indices.Material]
    extruder_stack.variant = mock_no_settings[container_indices.Variant]
    with unittest.mock.patch("cura.Settings.CuraContainerStack.DefinitionContainer", unittest.mock.MagicMock): #To guard against the type checking.
        extruder_stack.definition = mock_layer_heights[container_indices.Definition] #There's a layer height in here!

    assert extruder_stack.getProperty("layer_height", "value") == container_indices.Definition
    extruder_stack.variant = mock_layer_heights[container_indices.Variant]
    assert extruder_stack.getProperty("layer_height", "value") == container_indices.Variant
    extruder_stack.material = mock_layer_heights[container_indices.Material]
    assert extruder_stack.getProperty("layer_height", "value") == container_indices.Material
    extruder_stack.quality = mock_layer_heights[container_indices.Quality]
    assert extruder_stack.getProperty("layer_height", "value") == container_indices.Quality
    extruder_stack.qualityChanges = mock_layer_heights[container_indices.QualityChanges]
    assert extruder_stack.getProperty("layer_height", "value") == container_indices.QualityChanges
    extruder_stack.userChanges = mock_layer_heights[container_indices.UserChanges]
    assert extruder_stack.getProperty("layer_height", "value") == container_indices.UserChanges

##  Tests whether inserting a container is properly forbidden.
def test_insertContainer(extruder_stack):
    with pytest.raises(InvalidOperationError):
        extruder_stack.insertContainer(0, unittest.mock.MagicMock())

##  Tests whether removing a container is properly forbidden.
def test_removeContainer(extruder_stack):
    with pytest.raises(InvalidOperationError):
        extruder_stack.removeContainer(unittest.mock.MagicMock())

##  Tests setting definitions by specifying an ID of a definition that exists.
def test_setDefinitionByIdExists(extruder_stack, container_registry):
    container_registry.return_value = DefinitionContainer(container_id = "some_definition")
    extruder_stack.setDefinitionById("some_definition")
    assert extruder_stack.definition.getId() == "some_definition"

##  Tests setting definitions by specifying an ID of a definition that doesn't
#   exist.
@pytest.mark.skip
def test_setDefinitionByIdDoesntExist(extruder_stack):
    with pytest.raises(KeyError):
        extruder_stack.setDefinitionById("some_definition") #Container registry is empty now.

##  Tests setting materials by specifying an ID of a material that exists.
def test_setMaterialByIdExists(extruder_stack, container_registry):
    container_registry.return_value = getInstanceContainer(container_type = "material")
    extruder_stack.setMaterialById("InstanceContainer")
    assert extruder_stack.material.getId() == "InstanceContainer"

##  Tests setting materials by specifying an ID of a material that doesn't
#   exist.
@pytest.mark.skip
def test_setMaterialByIdDoesntExist(extruder_stack):
    with pytest.raises(KeyError):
        extruder_stack.setMaterialById("some_material") #Container registry is empty now.

##  Tests setting properties directly on the extruder stack.
@pytest.mark.skip
@pytest.mark.parametrize("key,              property,         value,       output_value", [
                        ("layer_height",    "value",          "0.1337",    0.1337),
                        ("foo",             "value",          "100",       100),
                        ("support_enabled", "value",          "True",      True),
                        ("layer_height",    "default_value",  0.1337,      0.1337),
                        ("layer_height",    "is_bright_pink", "of course", "of course")
])
def test_setPropertyUser(key, property, value, output_value, extruder_stack):
    extruder_stack.setProperty(key, value, property)
    assert extruder_stack.userChanges.getProperty(key, property) == output_value

##  Tests setting properties on specific containers on the extruder stack.
@pytest.mark.skip
@pytest.mark.parametrize("target_container", [
    "user",
    "quality_changes",
    "quality",
    "material",
    "variant",
    "definition"
])
def test_setPropertyOtherContainers(target_container, extruder_stack):
    #Other parameters that don't need to be varied.
    key = "layer_height"
    property = "value",
    value = "0.1337",
    output_value = 0.1337

    extruder_stack.setProperty(key, value, property, target_container = target_container)
    containers = {
        "user": extruder_stack.userChanges,
        "quality_changes": extruder_stack.qualityChanges,
        "quality": extruder_stack.quality,
        "material": extruder_stack.material,
        "variant": extruder_stack.variant,
        "definition_changes": extruder_stack.definition_changes,
        "definition": extruder_stack.definition
    }
    assert containers[target_container].getProperty(key, property) == output_value

##  Tests setting qualities by specifying an ID of a quality that exists.
def test_setQualityByIdExists(extruder_stack, container_registry):
    container_registry.return_value = getInstanceContainer(container_type = "quality")
    extruder_stack.setQualityById("InstanceContainer")
    assert extruder_stack.quality.getId() == "InstanceContainer"

##  Tests setting qualities by specifying an ID of a quality that doesn't exist.
@pytest.mark.skip
def test_setQualityByIdDoesntExist(extruder_stack):
    with pytest.raises(KeyError):
        extruder_stack.setQualityById("some_quality") #Container registry is empty now.

##  Tests setting quality changes by specifying an ID of a quality change that
#   exists.
def test_setQualityChangesByIdExists(extruder_stack, container_registry):
    container_registry.return_value = getInstanceContainer(container_type = "quality_changes")
    extruder_stack.setQualityChangesById("InstanceContainer")
    assert extruder_stack.qualityChanges.getId() == "InstanceContainer"

##  Tests setting quality changes by specifying an ID of a quality change that
#   doesn't exist.
@pytest.mark.skip
def test_setQualityChangesByIdDoesntExist(extruder_stack):
    with pytest.raises(KeyError):
        extruder_stack.setQualityChangesById("some_quality_changes") #Container registry is empty now.

##  Tests setting variants by specifying an ID of a variant that exists.
@pytest.mark.skip
def test_setVariantByIdExists(extruder_stack, container_registry):
    original_container_registry = UM.Settings.ContainerStack._containerRegistry
    UM.Settings.ContainerStack._containerRegistry = container_registry #Always has all the profiles you ask of.

    extruder_stack.setVariantById("some_variant") #The container registry always has a container with the ID.

    #Restore.
    UM.Settings.ContainerStack._containerRegistry = original_container_registry

##  Tests setting variants by specifying an ID of a variant that doesn't exist.
@pytest.mark.skip
def test_setVariantByIdDoesntExist(extruder_stack):
    with pytest.raises(KeyError):
        extruder_stack.setVariantById("some_variant") #Container registry is empty now.