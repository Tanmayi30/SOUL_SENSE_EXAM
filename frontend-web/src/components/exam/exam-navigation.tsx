'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight, Send } from 'lucide-react';
import { useExamStore } from '@/stores/examStore';
import { cn } from '@/lib/utils';

interface ExamNavigationProps {
  onSubmit: () => void;
  isSubmitting?: boolean;
  className?: string;
}

export const ExamNavigation: React.FC<ExamNavigationProps> = ({
  onSubmit,
  isSubmitting = false,
  className,
}) => {
  const {
    previousQuestion,
    nextQuestion,
    getIsFirstQuestion,
    getIsLastQuestion,
  } = useExamStore();

  const isFirst = getIsFirstQuestion();
  const isLast = getIsLastQuestion();

  return (
    <div className={cn('flex items-center justify-between', className)}>
      <Button
        variant="outline"
        onClick={previousQuestion}
        disabled={isFirst || isSubmitting}
        className="flex items-center gap-2"
      >
        <ChevronLeft className="h-4 w-4" />
        Previous
      </Button>

      <div className="flex items-center gap-2">
        {!isLast ? (
          <Button
            onClick={nextQuestion}
            disabled={isSubmitting}
            className="flex items-center gap-2"
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        ) : (
          <Button
            onClick={onSubmit}
            disabled={isSubmitting}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700"
          >
            {isSubmitting ? (
              <>
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                Submitting...
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                Submit Exam
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  );
};