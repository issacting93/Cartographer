import { Routes, Route, Link } from 'react-router-dom'
import BaselineChat from './pages/BaselineChat'
import TreatmentChat from './pages/TreatmentChat'
import ContextInventory from './pages/ContextInventory'
import Workspace from './pages/Workspace'
import AnnotationTool from './pages/AnnotationTool'

import TaskAnalytics from './pages/TaskAnalytics'

function HomePage() {

  return (
    <div className="min-h-screen bg-[var(--black)] flex items-center justify-center p-6">
      <div className="max-w-3xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-2 mb-4">
            <span className="material-symbols-rounded text-[var(--yellow)] text-4xl">hexagon</span>
            <h1 className="text-4xl font-bold text-white tracking-tight">
              CUI 2026
            </h1>
          </div>
          <p className="text-xl text-[var(--gray-dark)]">
            Tasks, Not Turns: Reframing Conversational Interfaces
          </p>
          <p className="text-[var(--gray-dark)] mt-2 text-sm">
            Comparative Evaluation Prototype
          </p>
        </div>

        {/* Evaluation Conditions */}
        <div className="mb-8">
          <h2 className="text-[var(--gray-dark)] text-xs uppercase tracking-widest mb-4 text-center">
            Evaluation Conditions
          </h2>
          <div className="grid md:grid-cols-2 gap-6">

            {/* Condition A: Baseline */}
            <Link
              to="/baseline"
              className="block p-6 bg-white bg-opacity-10 backdrop-blur-sm rounded-2xl border border-white border-opacity-20 hover:bg-opacity-20 transition-all"
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="material-symbols-rounded text-[var(--gray-dark)] text-2xl">chat</span>
                <div>
                  <span className="font-bold text-white block">Condition A</span>
                  <span className="text-[var(--gray-dark)] text-xs">Baseline</span>
                </div>
              </div>
              <p className="text-[var(--gray-dark)] text-sm mb-3">
                Chat-only interface. Constraints are mentioned once and scroll away.
                User must <strong className="text-white">type</strong> repairs from memory.
              </p>
              <div className="flex items-center gap-2 text-[var(--gray-dark)] text-xs">
                <span className="material-symbols-rounded text-sm">keyboard</span>
                Repair by typing
              </div>
            </Link>

            {/* Condition B: Treatment */}
            <Link
              to="/treatment"
              className="block p-6 bg-[var(--yellow)] rounded-2xl hover:scale-[1.02] transition-all"
            >
              <div className="flex items-center gap-3 mb-3">
                <span className="material-symbols-rounded text-[var(--black)] text-2xl">inventory_2</span>
                <div>
                  <span className="font-bold text-[var(--black)] block">Condition B</span>
                  <span className="text-[var(--black)] text-opacity-60 text-xs">Treatment</span>
                </div>
              </div>
              <p className="text-[var(--black)] text-opacity-80 text-sm mb-3">
                Chat + Context Inventory. Constraints are always visible in sidebar.
                User can <strong>click</strong> to reference constraints.
              </p>
              <div className="flex items-center gap-2 text-[var(--black)] text-opacity-60 text-xs">
                <span className="material-symbols-rounded text-sm">touch_app</span>
                Repair by clicking
              </div>
            </Link>
          </div>
        </div>

        {/* Scenario Card */}
        <div className="p-6 bg-white bg-opacity-5 rounded-2xl border border-white border-opacity-10">
          <h3 className="text-white font-bold mb-3 flex items-center gap-2">
            <span className="material-symbols-rounded text-[var(--yellow)]">work</span>
            Scenario: Career Coaching
          </h3>
          <p className="text-[var(--gray-dark)] text-sm mb-4">
            Work with an AI career coach to plan your next career move.
            At Turn 8, the AI will suggest a role that <strong className="text-[var(--orange)]">violates your constraints</strong>.
            How will you correct it?
          </p>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="px-3 py-2 rounded-full bg-white bg-opacity-5 border border-white border-opacity-10 text-[var(--gray-dark)] flex items-center gap-2">
              <span className="material-symbols-rounded text-sm text-[var(--green)]">flag</span>
              Goal: Senior engineering role
            </div>
            <div className="px-3 py-2 rounded-full bg-white bg-opacity-5 border border-white border-opacity-10 text-[var(--gray-dark)] flex items-center gap-2">
              <span className="material-symbols-rounded text-sm text-[var(--yellow)]">lock</span>
              Constraint: Max 45 hrs/week
            </div>
            <div className="px-3 py-2 rounded-full bg-white bg-opacity-5 border border-white border-opacity-10 text-[var(--gray-dark)] flex items-center gap-2">
              <span className="material-symbols-rounded text-sm text-[var(--yellow)]">lock</span>
              Constraint: Remote-first only
            </div>
            <div className="px-3 py-2 rounded-full bg-white bg-opacity-5 border border-white border-opacity-10 text-[var(--gray-dark)] flex items-center gap-2">
              <span className="material-symbols-rounded text-sm text-[var(--orange)]">favorite</span>
              Preference: Tech/AI sector
            </div>
          </div>
        </div>

        {/* Workspace Link - Primary */}
        <div className="mt-8 grid grid-cols-2 gap-6">
          <Link
            to="/workspace"
            className="block p-6 bg-gradient-to-r from-[var(--yellow)] to-[var(--orange)] rounded-2xl hover:scale-[1.02] transition-all text-center"
          >
            <div className="flex items-center justify-center gap-3 mb-2">
              <span className="material-symbols-rounded text-[var(--black)] text-3xl">dashboard</span>
              <span className="font-bold text-[var(--black)] text-xl">Workspace</span>
            </div>
            <p className="text-[var(--black)] text-opacity-70 text-sm">
              Tree-column context manager
            </p>
          </Link>

          <Link
            to="/analytics"
            className="block p-6 bg-[var(--black)] border border-white border-opacity-20 rounded-2xl hover:bg-white hover:bg-opacity-5 transition-all text-center group"
          >
            <div className="flex items-center justify-center gap-3 mb-2">
              <span className="material-symbols-rounded text-[var(--gray-dark)] group-hover:text-[var(--yellow)] transition-colors text-3xl">monitoring</span>
              <span className="font-bold text-white text-xl">Stability Landscape</span>
            </div>
            <p className="text-[var(--gray-dark)] text-sm">
              Scatter plot of N=983 interactions
            </p>
          </Link>
        </div>

        {/* Secondary Links */}
        <div className="mt-4 flex justify-center gap-6 text-sm">
          <Link
            to="/annotate"
            className="inline-flex items-center gap-2 text-[var(--gray-dark)] hover:text-white transition-colors"
          >
            <span className="material-symbols-rounded">edit_note</span>
            Annotation Tool
          </Link>
          <Link
            to="/context-inventory"
            className="inline-flex items-center gap-2 text-[var(--gray-dark)] hover:text-white transition-colors"
          >
            <span className="material-symbols-rounded">hexagon</span>
            Hex Grid Demo
          </Link>
        </div>

        <p className="text-center text-[var(--gray-dark)] text-xs mt-8 opacity-50">
          CUI 2026 Research Prototype
        </p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/baseline" element={<BaselineChat />} />
      <Route path="/treatment" element={<TreatmentChat />} />
      <Route path="/context-inventory" element={<ContextInventory />} />
      <Route path="/workspace" element={<Workspace />} />
      <Route path="/annotate" element={<AnnotationTool />} />
      <Route path="/analytics" element={<TaskAnalytics />} />
    </Routes>
  )
}

