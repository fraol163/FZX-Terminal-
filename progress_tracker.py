"""
Progress Tracker for AI Terminal Workflow
Comprehensive task and progress tracking with milestone system

Addresses user struggles:
- Losing track of what was accomplished
- Missing progress visualization
- Lack of milestone markers
- No resume guidance
"""

import os
import sys
import json
import time
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum

class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"

class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKLOG = 5

class MilestoneType(Enum):
    """Types of milestones."""
    FEATURE_COMPLETE = "feature_complete"
    BUG_FIXED = "bug_fixed"
    REFACTOR_COMPLETE = "refactor_complete"
    TESTING_COMPLETE = "testing_complete"
    DEPLOYMENT_READY = "deployment_ready"
    DOCUMENTATION_COMPLETE = "documentation_complete"
    PERFORMANCE_IMPROVED = "performance_improved"
    SECURITY_ENHANCED = "security_enhanced"

@dataclass
class Task:
    """Individual task representation."""
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    created_at: float
    updated_at: float
    completed_at: Optional[float] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    tags: List[str] = None
    dependencies: List[str] = None
    assignee: Optional[str] = None
    project_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    subtasks: List[str] = None
    notes: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.dependencies is None:
            self.dependencies = []
        if self.subtasks is None:
            self.subtasks = []
        if self.notes is None:
            self.notes = []

@dataclass
class Milestone:
    """Project milestone representation."""
    id: str
    title: str
    description: str
    milestone_type: MilestoneType
    achieved_at: float
    related_tasks: List[str]
    impact_score: float
    celebration_message: str
    next_steps: List[str] = None
    
    def __post_init__(self):
        if self.next_steps is None:
            self.next_steps = []

@dataclass
class ProgressSnapshot:
    """Progress snapshot at a point in time."""
    timestamp: float
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    completion_percentage: float
    velocity: float  # tasks per day
    estimated_completion: Optional[float] = None
    recent_achievements: List[str] = None
    
    def __post_init__(self):
        if self.recent_achievements is None:
            self.recent_achievements = []

class TaskManager:
    """Manages individual tasks and their lifecycle."""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_history: List[Dict[str, Any]] = []
        
    def create_task(self, title: str, description: str = "", 
                   priority: TaskPriority = TaskPriority.MEDIUM,
                   estimated_hours: Optional[float] = None,
                   tags: List[str] = None,
                   parent_task_id: Optional[str] = None) -> str:
        """Create a new task."""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        task = Task(
            id=task_id,
            title=title,
            description=description,
            status=TaskStatus.PENDING,
            priority=priority,
            created_at=time.time(),
            updated_at=time.time(),
            estimated_hours=estimated_hours,
            tags=tags or [],
            parent_task_id=parent_task_id
        )
        
        self.tasks[task_id] = task
        
        # Add to parent's subtasks if applicable
        if parent_task_id and parent_task_id in self.tasks:
            self.tasks[parent_task_id].subtasks.append(task_id)
            self.tasks[parent_task_id].updated_at = time.time()
        
        self._log_task_event(task_id, "created", {"title": title, "priority": priority.name})
        
        return task_id
    
    def update_task_status(self, task_id: str, new_status: TaskStatus, 
                          notes: str = "") -> bool:
        """Update task status."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        old_status = task.status
        task.status = new_status
        task.updated_at = time.time()
        
        if new_status == TaskStatus.COMPLETED:
            task.completed_at = time.time()
        
        if notes:
            task.notes.append(f"{datetime.now().isoformat()}: {notes}")
        
        self._log_task_event(task_id, "status_changed", {
            "old_status": old_status.name,
            "new_status": new_status.name,
            "notes": notes
        })
        
        return True
    
    def add_task_dependency(self, task_id: str, dependency_id: str) -> bool:
        """Add a dependency to a task."""
        if task_id not in self.tasks or dependency_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if dependency_id not in task.dependencies:
            task.dependencies.append(dependency_id)
            task.updated_at = time.time()
            
            self._log_task_event(task_id, "dependency_added", {"dependency": dependency_id})
        
        return True
    
    def get_task_progress(self, task_id: str) -> Dict[str, Any]:
        """Get detailed progress information for a task."""
        if task_id not in self.tasks:
            return {}
        
        task = self.tasks[task_id]
        
        # Calculate subtask progress
        subtask_progress = 0.0
        if task.subtasks:
            completed_subtasks = sum(
                1 for subtask_id in task.subtasks 
                if subtask_id in self.tasks and self.tasks[subtask_id].status == TaskStatus.COMPLETED
            )
            subtask_progress = completed_subtasks / len(task.subtasks)
        
        # Check dependency status
        blocked_by_dependencies = False
        if task.dependencies:
            for dep_id in task.dependencies:
                if dep_id in self.tasks and self.tasks[dep_id].status != TaskStatus.COMPLETED:
                    blocked_by_dependencies = True
                    break
        
        return {
            "task_id": task_id,
            "title": task.title,
            "status": task.status.name,
            "priority": task.priority.name,
            "progress_percentage": subtask_progress * 100,
            "subtasks_completed": len([s for s in task.subtasks if s in self.tasks and self.tasks[s].status == TaskStatus.COMPLETED]),
            "total_subtasks": len(task.subtasks),
            "blocked_by_dependencies": blocked_by_dependencies,
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            "days_since_created": (time.time() - task.created_at) / 86400,
            "last_updated": datetime.fromtimestamp(task.updated_at).isoformat()
        }
    
    def get_ready_tasks(self) -> List[str]:
        """Get tasks that are ready to be worked on (no blocking dependencies)."""
        ready_tasks = []
        
        for task_id, task in self.tasks.items():
            if task.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]:
                # Check if all dependencies are completed
                dependencies_met = all(
                    dep_id in self.tasks and self.tasks[dep_id].status == TaskStatus.COMPLETED
                    for dep_id in task.dependencies
                )
                
                if dependencies_met:
                    ready_tasks.append(task_id)
        
        # Sort by priority and creation time
        ready_tasks.sort(key=lambda tid: (
            self.tasks[tid].priority.value,
            self.tasks[tid].created_at
        ))
        
        return ready_tasks
    
    def _log_task_event(self, task_id: str, event_type: str, details: Dict[str, Any]) -> None:
        """Log task events for history tracking."""
        event = {
            "timestamp": time.time(),
            "task_id": task_id,
            "event_type": event_type,
            "details": details
        }
        
        self.task_history.append(event)
        
        # Keep only recent history
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-500:]

class MilestoneTracker:
    """Tracks project milestones and achievements."""
    
    def __init__(self):
        self.milestones: Dict[str, Milestone] = {}
        self.achievement_patterns = {
            MilestoneType.FEATURE_COMPLETE: [
                "All feature tasks completed",
                "Feature testing passed",
                "Feature documentation updated"
            ],
            MilestoneType.BUG_FIXED: [
                "Bug reproduction confirmed",
                "Fix implemented and tested",
                "Regression tests added"
            ],
            MilestoneType.REFACTOR_COMPLETE: [
                "Code restructured",
                "Tests still passing",
                "Performance maintained or improved"
            ]
        }
    
    def check_milestone_achievement(self, tasks: Dict[str, Task]) -> List[str]:
        """Check if any milestones have been achieved."""
        achieved_milestones = []
        
        # Check for feature completion
        feature_tasks = [t for t in tasks.values() if "feature" in t.tags]
        if feature_tasks and all(t.status == TaskStatus.COMPLETED for t in feature_tasks):
            milestone_id = self._create_milestone(
                "Feature Development Complete",
                "All feature tasks have been completed successfully",
                MilestoneType.FEATURE_COMPLETE,
                [t.id for t in feature_tasks],
                impact_score=0.8
            )
            achieved_milestones.append(milestone_id)
        
        # Check for bug fixing milestone
        bug_tasks = [t for t in tasks.values() if "bug" in t.tags or "fix" in t.tags]
        if len(bug_tasks) >= 5 and all(t.status == TaskStatus.COMPLETED for t in bug_tasks):
            milestone_id = self._create_milestone(
                "Bug Fixing Sprint Complete",
                f"Successfully resolved {len(bug_tasks)} bugs",
                MilestoneType.BUG_FIXED,
                [t.id for t in bug_tasks],
                impact_score=0.6
            )
            achieved_milestones.append(milestone_id)
        
        # Check for testing milestone
        test_tasks = [t for t in tasks.values() if "test" in t.tags]
        if test_tasks and all(t.status == TaskStatus.COMPLETED for t in test_tasks):
            milestone_id = self._create_milestone(
                "Testing Phase Complete",
                "All testing tasks have been completed",
                MilestoneType.TESTING_COMPLETE,
                [t.id for t in test_tasks],
                impact_score=0.7
            )
            achieved_milestones.append(milestone_id)
        
        return achieved_milestones
    
    def _create_milestone(self, title: str, description: str, 
                         milestone_type: MilestoneType, related_tasks: List[str],
                         impact_score: float) -> str:
        """Create a new milestone."""
        milestone_id = f"milestone_{uuid.uuid4().hex[:8]}"
        
        celebration_messages = {
            MilestoneType.FEATURE_COMPLETE: "🎉 Feature milestone achieved! Great progress on functionality!",
            MilestoneType.BUG_FIXED: "🐛 Bug squashing milestone! Code quality improved!",
            MilestoneType.TESTING_COMPLETE: "✅ Testing milestone reached! Quality assurance complete!",
            MilestoneType.REFACTOR_COMPLETE: "🔧 Refactoring milestone! Code structure improved!",
            MilestoneType.PERFORMANCE_IMPROVED: "⚡ Performance milestone! System optimization achieved!",
            MilestoneType.SECURITY_ENHANCED: "🔒 Security milestone! Protection measures strengthened!"
        }
        
        milestone = Milestone(
            id=milestone_id,
            title=title,
            description=description,
            milestone_type=milestone_type,
            achieved_at=time.time(),
            related_tasks=related_tasks,
            impact_score=impact_score,
            celebration_message=celebration_messages.get(milestone_type, "🎯 Milestone achieved!")
        )
        
        self.milestones[milestone_id] = milestone
        
        return milestone_id
    
    def get_recent_milestones(self, days: int = 7) -> List[Milestone]:
        """Get milestones achieved in the last N days."""
        cutoff_time = time.time() - (days * 86400)
        
        recent = [
            milestone for milestone in self.milestones.values()
            if milestone.achieved_at >= cutoff_time
        ]
        
        return sorted(recent, key=lambda m: m.achieved_at, reverse=True)

class ProgressAnalyzer:
    """Analyzes progress patterns and provides insights."""
    
    def __init__(self):
        self.snapshots: List[ProgressSnapshot] = []
        
    def create_snapshot(self, tasks: Dict[str, Task]) -> ProgressSnapshot:
        """Create a progress snapshot."""
        total_tasks = len(tasks)
        completed_tasks = len([t for t in tasks.values() if t.status == TaskStatus.COMPLETED])
        in_progress_tasks = len([t for t in tasks.values() if t.status == TaskStatus.IN_PROGRESS])
        blocked_tasks = len([t for t in tasks.values() if t.status == TaskStatus.BLOCKED])
        
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate velocity (tasks completed per day)
        velocity = self._calculate_velocity(tasks)
        
        # Estimate completion time
        remaining_tasks = total_tasks - completed_tasks
        estimated_completion = None
        if velocity > 0:
            days_remaining = remaining_tasks / velocity
            estimated_completion = time.time() + (days_remaining * 86400)
        
        snapshot = ProgressSnapshot(
            timestamp=time.time(),
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            in_progress_tasks=in_progress_tasks,
            blocked_tasks=blocked_tasks,
            completion_percentage=completion_percentage,
            velocity=velocity,
            estimated_completion=estimated_completion
        )
        
        self.snapshots.append(snapshot)
        
        # Keep only recent snapshots
        if len(self.snapshots) > 100:
            self.snapshots = self.snapshots[-50:]
        
        return snapshot
    
    def _calculate_velocity(self, tasks: Dict[str, Task]) -> float:
        """Calculate task completion velocity."""
        # Look at tasks completed in the last 7 days
        cutoff_time = time.time() - (7 * 86400)
        
        recent_completions = [
            t for t in tasks.values()
            if t.completed_at and t.completed_at >= cutoff_time
        ]
        
        return len(recent_completions) / 7.0  # tasks per day
    
    def get_progress_trends(self) -> Dict[str, Any]:
        """Analyze progress trends over time."""
        if len(self.snapshots) < 2:
            return {"insufficient_data": True}
        
        recent_snapshots = self.snapshots[-10:]
        
        # Calculate trends
        completion_trend = self._calculate_trend([s.completion_percentage for s in recent_snapshots])
        velocity_trend = self._calculate_trend([s.velocity for s in recent_snapshots])
        
        return {
            "completion_trend": completion_trend,
            "velocity_trend": velocity_trend,
            "current_velocity": recent_snapshots[-1].velocity,
            "completion_percentage": recent_snapshots[-1].completion_percentage,
            "estimated_completion": recent_snapshots[-1].estimated_completion,
            "trend_analysis": self._analyze_trends(completion_trend, velocity_trend)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from a series of values."""
        if len(values) < 2:
            return "stable"
        
        # Simple trend calculation
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        if second_half > first_half * 1.1:
            return "increasing"
        elif second_half < first_half * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _analyze_trends(self, completion_trend: str, velocity_trend: str) -> str:
        """Provide trend analysis and recommendations."""
        if completion_trend == "increasing" and velocity_trend == "increasing":
            return "Excellent progress! Both completion rate and velocity are improving."
        elif completion_trend == "increasing" and velocity_trend == "stable":
            return "Good steady progress. Consider optimizing workflow to increase velocity."
        elif completion_trend == "stable" and velocity_trend == "decreasing":
            return "Progress has plateaued. Consider addressing blockers or breaking down large tasks."
        elif completion_trend == "decreasing":
            return "Progress is slowing. Review current tasks and remove blockers."
        else:
            return "Progress is steady. Maintain current momentum."

class ProgressTracker:
    """Main progress tracking system."""
    
    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.progress_file = self.project_root / ".terminal_data" / "progress.json"
        
        self.task_manager = TaskManager()
        self.milestone_tracker = MilestoneTracker()
        self.progress_analyzer = ProgressAnalyzer()
        
        self._load_progress_data()
    
    def create_task(self, title: str, description: str = "", 
                   priority: str = "medium", estimated_hours: Optional[float] = None,
                   tags: List[str] = None) -> str:
        """Create a new task."""
        priority_enum = TaskPriority[priority.upper()]
        return self.task_manager.create_task(title, description, priority_enum, estimated_hours, tags)
    
    def update_task(self, task_id: str, status: str, notes: str = "") -> bool:
        """Update task status."""
        status_enum = TaskStatus[status.upper()]
        success = self.task_manager.update_task_status(task_id, status_enum, notes)
        
        if success:
            # Check for milestone achievements
            achieved = self.milestone_tracker.check_milestone_achievement(self.task_manager.tasks)
            for milestone_id in achieved:
                milestone = self.milestone_tracker.milestones[milestone_id]
                print(f"\n{milestone.celebration_message}")
                print(f"Milestone: {milestone.title}")
            
            # Create progress snapshot
            self.progress_analyzer.create_snapshot(self.task_manager.tasks)
            
            # Save progress
            self._save_progress_data()
        
        return success
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive progress dashboard."""
        tasks = self.task_manager.tasks
        
        # Current snapshot
        current_snapshot = self.progress_analyzer.create_snapshot(tasks)
        
        # Ready tasks
        ready_tasks = self.task_manager.get_ready_tasks()
        
        # Recent milestones
        recent_milestones = self.milestone_tracker.get_recent_milestones(7)
        
        # Progress trends
        trends = self.progress_analyzer.get_progress_trends()
        
        return {
            "current_progress": {
                "total_tasks": current_snapshot.total_tasks,
                "completed_tasks": current_snapshot.completed_tasks,
                "completion_percentage": current_snapshot.completion_percentage,
                "velocity": current_snapshot.velocity
            },
            "ready_tasks": [
                {
                    "id": task_id,
                    "title": tasks[task_id].title,
                    "priority": tasks[task_id].priority.name
                }
                for task_id in ready_tasks[:5]
            ],
            "recent_milestones": [
                {
                    "title": m.title,
                    "type": m.milestone_type.name,
                    "achieved_at": datetime.fromtimestamp(m.achieved_at).strftime("%Y-%m-%d"),
                    "impact_score": m.impact_score
                }
                for m in recent_milestones[:3]
            ],
            "trends": trends,
            "recommendations": self._generate_recommendations(current_snapshot, ready_tasks, trends)
        }
    
    def _generate_recommendations(self, snapshot: ProgressSnapshot, 
                                ready_tasks: List[str], trends: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if snapshot.blocked_tasks > 0:
            recommendations.append(f"Address {snapshot.blocked_tasks} blocked tasks to improve flow")
        
        if len(ready_tasks) > 10:
            recommendations.append("Consider breaking down large tasks - many tasks are ready")
        elif len(ready_tasks) == 0:
            recommendations.append("No ready tasks available - check dependencies")
        
        if snapshot.velocity < 1.0:
            recommendations.append("Low velocity detected - consider reducing task complexity")
        
        if trends.get("completion_trend") == "decreasing":
            recommendations.append("Progress is slowing - review current approach")
        
        if snapshot.completion_percentage > 80:
            recommendations.append("Nearing completion! Focus on final tasks and testing")
        
        return recommendations
    
    def _load_progress_data(self) -> None:
        """Load progress data from disk."""
        try:
            if self.progress_file.exists():
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Load tasks
                for task_data in data.get("tasks", []):
                    task = Task(**task_data)
                    task.status = TaskStatus(task_data["status"])
                    task.priority = TaskPriority(task_data["priority"])
                    self.task_manager.tasks[task.id] = task
                
                # Load milestones
                for milestone_data in data.get("milestones", []):
                    milestone = Milestone(**milestone_data)
                    milestone.milestone_type = MilestoneType(milestone_data["milestone_type"])
                    self.milestone_tracker.milestones[milestone.id] = milestone
                
                print("✓ Progress data loaded")
        
        except Exception as e:
            print(f"⚠ Could not load progress data: {e}")
    
    def _save_progress_data(self) -> None:
        """Save progress data to disk."""
        try:
            self.progress_file.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "timestamp": datetime.now().isoformat(),
                "tasks": [asdict(task) for task in self.task_manager.tasks.values()],
                "milestones": [asdict(milestone) for milestone in self.milestone_tracker.milestones.values()],
                "snapshots": [asdict(snapshot) for snapshot in self.progress_analyzer.snapshots[-10:]]
            }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        
        except Exception as e:
            print(f"⚠ Could not save progress data: {e}")

# Global progress tracker instance
_progress_tracker_instance = None

def get_progress_tracker() -> ProgressTracker:
    """Get the global progress tracker instance."""
    global _progress_tracker_instance
    if _progress_tracker_instance is None:
        _progress_tracker_instance = ProgressTracker()
    return _progress_tracker_instance

if __name__ == "__main__":
    print("📊 Testing Progress Tracker...")
    
    tracker = get_progress_tracker()
    
    # Create some test tasks
    task1 = tracker.create_task("Implement user authentication", "Add login/logout functionality", "high", 8.0, ["feature", "security"])
    task2 = tracker.create_task("Write unit tests", "Add comprehensive test coverage", "medium", 4.0, ["test"])
    task3 = tracker.create_task("Fix login bug", "Resolve authentication issue", "critical", 2.0, ["bug", "fix"])
    
    print(f"Created tasks: {task1}, {task2}, {task3}")
    
    # Update task statuses
    tracker.update_task(task1, "in_progress", "Started implementation")
    tracker.update_task(task3, "completed", "Bug fixed and tested")
    
    # Get dashboard
    dashboard = tracker.get_dashboard()
    
    print(f"\n📈 Progress Dashboard:")
    print(f"  Total tasks: {dashboard['current_progress']['total_tasks']}")
    print(f"  Completed: {dashboard['current_progress']['completed_tasks']}")
    print(f"  Completion: {dashboard['current_progress']['completion_percentage']:.1f}%")
    print(f"  Velocity: {dashboard['current_progress']['velocity']:.2f} tasks/day")
    
    if dashboard['ready_tasks']:
        print(f"\n📋 Ready tasks:")
        for task in dashboard['ready_tasks']:
            print(f"    • {task['title']} ({task['priority']})")
    
    if dashboard['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in dashboard['recommendations']:
            print(f"    • {rec}")
    
    print("\n✅ Progress Tracker test completed!")