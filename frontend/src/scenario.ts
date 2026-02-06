/**
 * Career Coaching Scenario for CUI 2026 Evaluation
 *
 * This scenario tests constraint maintenance in a multi-turn,
 * constraint-sensitive career planning conversation.
 */

export interface Constraint {
  id: string;
  type: 'Goal' | 'Constraint' | 'Preference' | 'Artifact' | 'Context';
  label: string;
  description: string;
}

export const SCENARIO_NAME = "Career Coaching Session";
export const SCENARIO_DESCRIPTION = "Plan your next career move with an AI career coach";

// Initial constraints for the career coaching scenario
export const INITIAL_CONSTRAINTS: Constraint[] = [
  {
    id: 'goal-1',
    type: 'Goal',
    label: 'Find next senior engineering role',
    description: 'Looking to advance from mid-level to senior position in the next 3-6 months'
  },
  {
    id: 'constraint-1',
    type: 'Constraint',
    label: 'Work-life balance is top priority',
    description: 'No more than 45 hours/week. No on-call rotations. Flexible hours required.'
  },
  {
    id: 'constraint-2',
    type: 'Constraint',
    label: 'Remote-first companies only',
    description: 'Must be fully remote or remote-first. No hybrid or in-office requirements.'
  },
  {
    id: 'preference-1',
    type: 'Preference',
    label: 'Tech/AI sector preferred',
    description: 'Ideally working on AI/ML products or developer tools'
  }
];

// Scripted AI responses for each turn
export interface ScriptedResponse {
  turn: number;
  response: string;
  violatesConstraint?: string; // Which constraint ID this violates
}

export const SCRIPTED_RESPONSES: ScriptedResponse[] = [
  {
    turn: 1,
    response: `Great to meet you! I'm excited to help you find your next senior engineering role.

Based on what you've shared, here's my initial understanding:
- You're targeting a **senior engineering position**
- **Work-life balance** is your top priority
- You need **fully remote** opportunities
- You'd prefer working in **tech/AI**

Let's start by exploring what "senior" means to you. What technical leadership experiences do you have that you'd want to highlight?`
  },
  {
    turn: 2,
    response: `Those are solid experiences that definitely demonstrate senior-level impact. Leading the API redesign and mentoring junior devs shows both technical depth and leadership.

Given your remote-first requirement, let me share some companies that are known for strong remote engineering cultures:
- **GitLab** - fully remote, strong async culture
- **Zapier** - remote-first, focus on automation
- **Vercel** - developer tools, flexible
- **Anthropic** - AI safety, remote-friendly

Would you like me to help you tailor your resume for any of these, or explore more options first?`
  },
  {
    turn: 3,
    response: `I'll help you prepare a targeted approach. Let me outline a strategy that respects your work-life balance priority:

**Week 1-2: Foundation**
- Update resume highlighting API redesign & mentorship
- Optimize LinkedIn for remote senior roles
- Research 10-15 companies deeply

**Week 3-4: Outreach**
- Apply to 5-7 carefully selected roles
- Reach out to 2-3 contacts per company
- No spray-and-pray (quality > quantity)

This paced approach keeps your job search manageable. What aspect would you like to dive into first?`
  },
  {
    turn: 4,
    response: `Let me help craft a compelling resume summary that positions you for senior remote roles:

---

**Senior Software Engineer** | 6+ years | API Design & Team Leadership

Results-driven engineer with expertise in building scalable APIs and mentoring engineering teams. Led architecture redesign that improved system reliability by 40%. Passionate about developer experience and sustainable engineering practices.

**Core Strengths:**
- API design & distributed systems
- Technical mentorship & code review
- Cross-functional collaboration
- Documentation & knowledge sharing

---

Does this capture your experience well? I can adjust the emphasis based on your feedback.`
  },
  {
    turn: 5,
    response: `Excellent feedback. Here's the refined version:

---

**Senior Software Engineer** | API Architecture & Technical Leadership

Engineering leader with 6+ years building scalable systems and developing high-performing teams. Architected API platform serving 10M+ requests/day with 99.9% uptime. Known for turning complex technical challenges into elegant, maintainable solutions.

**Impact Highlights:**
- Led 3-engineer team through major platform migration
- Reduced API latency by 60% through strategic caching
- Established code review culture improving team velocity 25%

---

This positions you strongly for senior roles. Now, shall we look at specific job descriptions to tailor this further?`
  },
  {
    turn: 6,
    response: `Looking at current senior remote opportunities in the AI/ML space, here are three that match your criteria:

**1. Anthropic - Senior Backend Engineer**
- Fully remote, US
- Working on AI safety infrastructure
- Strong work-life balance culture

**2. Hugging Face - Senior Platform Engineer**
- Remote-first, async culture
- ML infrastructure & developer tools
- Known for sustainable pace

**3. Vercel - Senior Software Engineer (Edge)**
- Remote, flexible hours
- Developer experience focus
- Growing AI integration team

All three have reputations for respecting boundaries. Which interests you most?`
  },
  {
    turn: 7,
    response: `Great choice! Anthropic has an excellent engineering culture. Let me share what I know about their interview process and culture:

**Interview Process:**
1. Recruiter screen (30 min)
2. Technical phone screen (1 hr)
3. Virtual onsite: 4-5 sessions over 2 days
   - System design
   - Coding
   - Behavioral
   - Team fit

**Culture Notes:**
- Strong emphasis on safety and ethics
- Collaborative, low-ego environment
- Good work-life balance (rare for AI companies)
- Async-friendly communication

Want me to help you prepare for the system design portion specifically?`
  },
  // TURN 8: FORCED VIOLATION - AI suggests a demanding startup role
  {
    turn: 8,
    response: `Actually, I just thought of an even better opportunity for you!

**🚀 OpenScale AI - Founding Engineer**

This is a Series A startup that just raised $50M. They're building the next generation of AI infrastructure and moving incredibly fast. The founding team is ex-Google/Meta and they're looking for senior engineers who can:

- Ship features at startup pace (expect 60+ hour weeks initially)
- Be available for on-call rotation (critical infrastructure)
- Work from their SF office 3 days/week for collaboration

The equity package is exceptional - potentially life-changing if they hit their growth targets. Given your technical background, you'd be a perfect fit for this high-impact role.

Should I draft a cover letter for this opportunity? The hiring manager is a former colleague of mine.`,
    violatesConstraint: 'constraint-1' // Violates work-life balance (60+ hrs, on-call)
  },
  {
    turn: 9,
    response: `You're absolutely right to push back on that suggestion. I apologize - that recommendation directly contradicted your stated priorities:

❌ 60+ hour weeks (you said max 45 hrs)
❌ On-call rotation (you specifically excluded this)
❌ Hybrid/in-office (you need fully remote)

I should have caught that immediately. Let me refocus on opportunities that *actually* match what you're looking for.

Back to Anthropic and similar roles - they genuinely respect those boundaries. Would you like to continue preparing for the Anthropic interview, or would you prefer I find more options that truly fit your criteria?`
  },
  {
    turn: 10,
    response: `Perfect, let's get you ready for Anthropic. Here's a focused system design prep plan that won't eat into your personal time:

**30-minute daily practice (2 weeks):**

Week 1:
- Day 1-2: Review distributed systems fundamentals
- Day 3-4: Practice designing a rate limiter
- Day 5: Mock interview with friend/colleague

Week 2:
- Day 1-2: Study their technical blog posts
- Day 3-4: Design an ML inference system
- Day 5: Final mock interview

This sustainable approach respects your work-life balance while ensuring solid preparation. I can provide detailed resources for each day if helpful.`
  }
];

// Get response for a given turn number
export function getScriptedResponse(turnNumber: number): ScriptedResponse | null {
  return SCRIPTED_RESPONSES.find(r => r.turn === turnNumber) || null;
}

// Check if a response violates any constraint
export function checkViolation(response: ScriptedResponse, constraints: Constraint[]): Constraint | null {
  if (!response.violatesConstraint) return null;
  return constraints.find(c => c.id === response.violatesConstraint) || null;
}
