import c4d

def delete_hidden_objects(obj):
    """
    Recursively deletes all objects that are hidden in the editor.

    Args:
        obj (c4d.BaseObject): The object to start the check from.
    """
    if obj is None:
        return

    # Get the next object before possibly deleting the current, to maintain valid iteration
    next_obj = obj.GetNext()
    child = obj.GetDown()
    
    # Check if this object is hidden in the editor
    visibility = obj[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR]
    if visibility == c4d.MODE_OFF:  # Hidden in the editor
        doc.AddUndo(c4d.UNDOTYPE_DELETE, obj)  # Add undo support
        obj.Remove()  # Remove the object
    
    # Process children (if any)
    if child is not None:
        delete_hidden_objects(child)
    
    # Process the next sibling object
    delete_hidden_objects(next_obj)

def main():
    """
    Main entry point of the script.
    Deletes all hidden objects in the active Cinema 4D document.
    """
    doc.StartUndo()  # Start recording undo actions
    
    # Get the first object in the scene's hierarchy
    obj = doc.GetFirstObject()
    
    # Recursively delete all hidden objects
    delete_hidden_objects(obj)
    
    doc.EndUndo()  # End recording undo actions
    c4d.EventAdd()  # Refresh the scene to reflect changes

# Boilerplate code to ensure the script is executed correctly in Cinema 4D
if __name__ == '__main__':
    main()