/**
 * Workspace.tsx - CUI 2026
 * 
 * Three-panel workspace interface:
 * - Left: Context source (drag from)
 * - Center: Conversation or canvas
 * - Right: Details + create session context
 */

import { ThreePanelLayout } from '../components/ThreePanelLayout';
import { ContextSourcePanel } from '../components/ContextSourcePanel';
import { WorkspacePanel } from '../components/WorkspacePanel';
import { DetailsPanel } from '../components/DetailsPanel';

export default function Workspace() {
    return (
        <ThreePanelLayout
            title="Context Workspace"
            leftPanel={<ContextSourcePanel />}
            centerPanel={<WorkspacePanel />}
            rightPanel={<DetailsPanel />}
        />
    );
}
