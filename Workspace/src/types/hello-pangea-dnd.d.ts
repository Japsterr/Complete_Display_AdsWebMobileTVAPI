declare module '@hello-pangea/dnd' {
  import * as React from 'react';
  export interface DragDropContextProps { onDragEnd: (result: DropResult) => void; children?: React.ReactNode; }
  export class DragDropContext extends React.Component<DragDropContextProps> {}
  export interface DroppableProvided { innerRef: (el: HTMLElement | null) => any; droppableProps: any; placeholder: React.ReactNode; }
  export interface DroppableStateSnapshot { isDraggingOver: boolean; }
  export interface DroppableProps { droppableId: string; children: (provided: DroppableProvided, snapshot: DroppableStateSnapshot) => React.ReactNode; }
  export class Droppable extends React.Component<DroppableProps> {}
  export interface DraggableProvided { innerRef: (el: HTMLElement | null) => any; draggableProps: any; dragHandleProps: any; }
  export interface DraggableStateSnapshot { isDragging: boolean; }
  export interface DraggableProps { draggableId: string; index: number; children: (provided: DraggableProvided, snapshot: DraggableStateSnapshot) => React.ReactNode; }
  export class Draggable extends React.Component<DraggableProps> {}
  export interface DropResult { source: { index: number; droppableId: string }; destination?: { index: number; droppableId: string } | null; draggableId: string; type?: string; }
}
