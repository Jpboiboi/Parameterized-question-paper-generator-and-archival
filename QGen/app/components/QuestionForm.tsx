interface NumericalQuestion {
  questionText: string;
  variables: {
    [key: string]: {
      min: number;
      max: number;
      step?: number;
    }
  };
  answerExpression: string;
  generatedValues?: {
    [key: string]: number;
  };
}

function generateVariables(question: NumericalQuestion): NumericalQuestion {
  const generated: { [key: string]: number } = {};
  
  for (const [varName, config] of Object.entries(question.variables)) {
    const range = config.max - config.min;
    const steps = config.step ? Math.floor(range / config.step) : range;
    generated[varName] = config.min + 
      Math.round(Math.random() * steps) * (config.step || 1);
  }
  
  return {
    ...question,
    generatedValues: generated
  };
}

function calculateAnswer(question: NumericalQuestion): number {
  if (!question.generatedValues) return NaN;
  const vars = question.generatedValues;
  // Simple expression evaluator using generated values
  return Function(...Object.keys(vars), `return ${question.answerExpression}`)
    (...Object.values(vars));
} 