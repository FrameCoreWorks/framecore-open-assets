# Semantic cue taxonomy

UI SFX names what happened, not what the sound resembles. Each cue should carry the same intent across every feel pack.

## Input

| Cue | Use it for | Do not use it for |
| --- | --- | --- |
| `hover` | Fine-pointer discovery on sparse, important controls | Touch interfaces or every item in a dense table |
| `press` | Pointer or key down on a physical-feeling control | The completed action outcome |
| `release` | Pointer or key up, especially press-and-hold controls | Success confirmation |
| `double-click` | A recognized rapid secondary activation | Two unrelated clicks |
| `focus` | A control becomes ready for keyboard or text input | Pointer hover without focus |
| `long-press` | A sustained press reveals a secondary action | An ordinary primary activation |

## Selection

| Cue | Use it for | Do not use it for |
| --- | --- | --- |
| `select` | Choosing a tab, option, item, or tool | Turning on a binary setting |
| `deselect` | Removing an item from the active set | Closing the surrounding view |
| `toggle-on` | A setting changes from off to on | General selection |
| `toggle-off` | A setting changes from on to off | Errors or blocked settings |
| `check` | A checkbox or task becomes complete | General success across a whole flow |
| `uncheck` | A checkbox or task becomes incomplete | Undoing unrelated content edits |

## Navigation

| Cue | Use it for | Do not use it for |
| --- | --- | --- |
| `open` | Menus, sheets, panels, detail views | Starting a background process |
| `close` | Dismissing a layer or collapsing detail | Stopping media |
| `back` | Returning to the previous place | Undoing data changes |
| `forward` | Advancing to the next place | Completing a multi-step flow |
| `expand` | Revealing detail inside a collapsed region | Opening a separate navigation layer |
| `collapse` | Returning detail to its compact state | Closing the surrounding view |

## Editing

| Cue | Use it for | Do not use it for |
| --- | --- | --- |
| `delete` | A destructive removal that has been committed | A removable selection before confirmation |
| `cancel` | Abandoning a pending action without applying it | Closing an ordinary navigation layer |
| `undo` | Reversing the most recent change | Back navigation |
| `redo` | Reapplying a reversed change | Retrying a failed network request |
| `copy` | Placing selected content on the clipboard | Duplicating an object immediately |
| `paste` | Inserting clipboard content | Uploading or importing a file |

## Movement

| Cue | Use it for | Do not use it for |
| --- | --- | --- |
| `drag-start` | An object lifting into a dragged state | Every pointer move |
| `drop` | A dragged object landing in a valid target | Invalid drops, which need `error` or `blocked` UI |
| `snap` | Alignment, docking, or grid lock | General selection |
| `swipe` | Spatial touch navigation | Ordinary scrolling |
| `reorder` | An item settles into a new sequence position | Every drag movement frame |
| `invalid-drop` | A dragged object cannot land in the target | A general validation error |

## Communication

| Cue | Use it for | Do not use it for |
| --- | --- | --- |
| `send` | A message or shared object 