import React, { useState, useEffect } from "react";
import Joyride from "react-joyride";

function Tour() {
  const [run, setRun] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem("tourComplete")) {
      setRun(true);
    }
  }, []);

  const steps = [
    {
      target: "#tab-overview",
      content: "Start here for a case overview and metrics.",
    },
    {
      target: "#tab-upload",
      content: "Upload discovery documents for analysis.",
    },
    {
      target: "#tab-pipeline",
      content: "Track progress as documents move through the pipeline.",
    },
    {
      target: "#tab-theory",
      content: "Review AI-suggested case theories and evidence.",
    },
  ];

  const handle = (data) => {
    const { status } = data;
    if (["finished", "skipped"].includes(status)) {
      localStorage.setItem("tourComplete", "true");
      setRun(false);
    }
  };

  return (
    <Joyride
      steps={steps}
      run={run}
      continuous
      showSkipButton
      callback={handle}
      styles={{ options: { zIndex: 10000 } }}
    />
  );
}

export default Tour;
