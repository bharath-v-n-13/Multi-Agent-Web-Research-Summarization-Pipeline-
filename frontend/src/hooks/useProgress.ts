import { useState, useEffect, useRef } from "react";
import type { AgentStepProgress } from "../types/research";

const AGENT_STEPS: { agent: AgentStepProgress["agent"]; duration: number; messages: string[] }[] = [
  {
    agent: "planner",
    duration: 3000,
    messages: [
      "Planner started: Analyzing topic...",
      "Selecting query strategy based on research depth...",
      "Formulating 3-8 search queries for the local index...",
      "Planner finished. Generated 5 queries."
    ]
  },
  {
    agent: "searcher",
    duration: 5000,
    messages: [
      "Searcher started: Indexing collection...",
      "Executing BM25 queries against 10,000 webpages...",
      "Merging query result lists and running deduplication...",
      "Scraping and cleaning raw HTML files...",
      "Searcher finished. 15 normalized documents retrieved."
    ]
  },
  {
    agent: "synthesizer",
    duration: 7000,
    messages: [
      "Synthesizer started: Parsing text bodies...",
      "Drafting executive summary...",
      "Resolving conflicting data blocks...",
      "Compiling citations and source indexes...",
      "Synthesizer finished. Compiled report sections."
    ]
  },
  {
    agent: "critic",
    duration: 5000,
    messages: [
      "Critic started: Inspecting report coverage...",
      "Evaluating content confidence score...",
      "Checking for bias and knowledge gaps...",
      "Verification complete: Confidence 92%. No gaps.",
      "Critic finished. Transitioning to complete."
    ]
  }
];

export const useProgress = (isProcessing: boolean, isSuccess: boolean, isError: boolean) => {
  const [currentStepIdx, setCurrentStepIdx] = useState<number>(0);
  const [currentMessageIdx, setCurrentMessageIdx] = useState<number>(0);
  const [status, setStatus] = useState<AgentStepProgress["status"]>("idle");
  const [iteration, setIteration] = useState<number>(0);
  const [elapsedTime, setElapsedTime] = useState<number>(0);
  
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const elapsedTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Track elapsed time
  useEffect(() => {
    if (isProcessing) {
      setElapsedTime(0);
      elapsedTimerRef.current = setInterval(() => {
        setElapsedTime((prev) => prev + 1);
      }, 1000);
    } else {
      if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
    }
    return () => {
      if (elapsedTimerRef.current) clearInterval(elapsedTimerRef.current);
    };
  }, [isProcessing]);

  // Handle agent workflow transitions
  useEffect(() => {
    if (!isProcessing) {
      if (isSuccess) {
        setStatus("completed");
        setCurrentStepIdx(AGENT_STEPS.length); // Completed state
      } else if (isError) {
        setStatus("failed");
      } else {
        setStatus("idle");
        setCurrentStepIdx(0);
        setCurrentMessageIdx(0);
        setIteration(0);
      }
      if (timerRef.current) clearTimeout(timerRef.current);
      return;
    }

    setStatus("running");
    setCurrentStepIdx(0);
    setCurrentMessageIdx(0);
    setIteration(0);

    let stepIdx = 0;
    let msgIdx = 0;

    const runTimeline = () => {
      if (stepIdx >= AGENT_STEPS.length) {
        // Just cycle messaging inside the Critic/Synthesizer until API returns
        setCurrentMessageIdx(AGENT_STEPS[AGENT_STEPS.length - 1].messages.length - 1);
        return;
      }

      const currentStep = AGENT_STEPS[stepIdx];
      setCurrentStepIdx(stepIdx);
      
      // Select message
      if (msgIdx < currentStep.messages.length) {
        setCurrentMessageIdx(msgIdx);
        
        // Schedule next message in the current agent step
        const messageInterval = currentStep.duration / currentStep.messages.length;
        timerRef.current = setTimeout(() => {
          msgIdx++;
          runTimeline();
        }, messageInterval);
      } else {
        // Move to the next agent
        stepIdx++;
        msgIdx = 0;
        
        // Simulating search iterations loop
        if (currentStep.agent === "critic" && Math.random() > 0.6 && iteration < 1) {
          // Critique triggers research loopback simulation!
          setIteration((prev) => prev + 1);
          stepIdx = 1; // Go back to Searcher
        }
        
        runTimeline();
      }
    };

    runTimeline();

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [isProcessing, isSuccess, isError]);

  const stepsList: AgentStepProgress[] = AGENT_STEPS.map((step, idx) => {
    let stepStatus: AgentStepProgress["status"] = "idle";
    let stepMessage = "";

    if (status === "completed") {
      stepStatus = "completed";
      stepMessage = step.messages[step.messages.length - 1];
    } else if (status === "failed") {
      if (idx === currentStepIdx) {
        stepStatus = "failed";
        stepMessage = "Workflow execution interrupted due to backend error.";
      } else if (idx < currentStepIdx) {
        stepStatus = "completed";
        stepMessage = step.messages[step.messages.length - 1];
      }
    } else if (status === "running") {
      if (idx < currentStepIdx) {
        stepStatus = "completed";
        stepMessage = step.messages[step.messages.length - 1];
      } else if (idx === currentStepIdx) {
        stepStatus = "running";
        stepMessage = step.messages[currentMessageIdx];
      }
    }

    return {
      agent: step.agent,
      status: stepStatus,
      message: stepMessage || (stepStatus === "idle" ? `Waiting for ${step.agent}...` : ""),
      iteration: idx >= 1 && idx <= 3 ? iteration : 0
    };
  });

  const currentAgent = currentStepIdx < AGENT_STEPS.length ? AGENT_STEPS[currentStepIdx].agent : "completed";
  const progressPercent = Math.min(
    status === "completed" ? 100 : Math.round((currentStepIdx / AGENT_STEPS.length) * 100),
    95
  );

  return {
    steps: stepsList,
    currentAgent,
    progressPercent: status === "completed" ? 100 : progressPercent,
    elapsedTime,
    status,
    iteration
  };
};
