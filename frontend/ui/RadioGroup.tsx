export default function RadioGroup({ children }: { children: React.ReactNode }) {
  return <div className="space-y-2">{children}</div>
}

/*

Notes for my teammates:

This is a reusable RadioGroup component that can be used to group radio buttons together.

What is a radio button group?

A radio button group is a set of radio buttons where only one button can be selected at a time. 
It is used when you want to allow users to choose one option from a predefined set of options. 
Each radio button in the group represents a different option, and selecting one will 
automatically deselect any previously selected button in the same group.

What could we use this for?

We could use a radio button group for various purposes, such as:

1. Selecting a intake form option (e.g., "Have allergies?" with options "Yes" and "No").

Maybe for the instak form we could have radio groups instead of text cuz i feel like 
thats easier to parse and process to the LLM and our whole pipeline that having to extract meaning 
from free text input

*/