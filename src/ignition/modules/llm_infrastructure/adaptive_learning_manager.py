"""Adaptive Learning Manager - Phase 13.3: Adaptive Learning & Feedback System.

Main orchestrator for continuous learning infrastructure with:
- Feedback collection system with user interaction tracking
- Online learning pipeline with incremental model updates
- Personalization and user-specific customization
- Performance monitoring and bias detection

Following crawl_mcp.py methodology for systematic development.
"""

import json
import logging
import os
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, validator

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class AdaptiveLearningValidationError(Exception):
    """Custom exception for adaptive learning validation errors."""

    pass


class FeedbackCollectionConfig(BaseModel):
    """Step 2: Input validation for feedback collection (crawl_mcp.py methodology)."""

    collection_enabled: bool = Field(
        default=True, description="Enable feedback collection"
    )
    interaction_tracking: bool = Field(
        default=True, description="Enable interaction tracking"
    )
    quality_threshold: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Quality threshold for feedback"
    )
    batch_size: int = Field(
        default=100, ge=1, le=1000, description="Batch size for processing"
    )
    retention_days: int = Field(
        default=90, ge=1, le=365, description="Data retention period"
    )
    anonymization_enabled: bool = Field(
        default=True, description="Enable data anonymization"
    )

    @validator("quality_threshold")
    def validate_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Quality threshold must be between 0.0 and 1.0")
        return v


class OnlineLearningConfig(BaseModel):
    """Step 2: Input validation for online learning (crawl_mcp.py methodology)."""

    incremental_updates: bool = Field(
        default=True, description="Enable incremental updates"
    )
    update_frequency_hours: int = Field(
        default=24, ge=1, le=168, description="Update frequency in hours"
    )
    performance_threshold: float = Field(
        default=0.05, ge=0.01, le=0.20, description="Performance improvement threshold"
    )
    rollback_enabled: bool = Field(
        default=True, description="Enable automatic rollback"
    )
    a_b_testing: bool = Field(default=True, description="Enable A/B testing")
    max_concurrent_models: int = Field(
        default=3, ge=1, le=10, description="Maximum concurrent models"
    )

    @validator("performance_threshold")
    def validate_performance_threshold(cls, v):
        if not 0.01 <= v <= 0.20:
            raise ValueError("Performance threshold must be between 0.01 and 0.20")
        return v


class PersonalizationConfig(BaseModel):
    """Step 2: Input validation for personalization (crawl_mcp.py methodology)."""

    user_profiles: bool = Field(default=True, description="Enable user profiles")
    experience_levels: list[str] = Field(
        default=["beginner", "intermediate", "expert"], description="Experience levels"
    )
    response_styles: list[str] = Field(
        default=["concise", "detailed", "step_by_step"], description="Response styles"
    )
    domain_specialization: bool = Field(
        default=True, description="Enable domain specialization"
    )
    cultural_adaptation: bool = Field(
        default=False, description="Enable cultural adaptation"
    )
    accessibility_features: bool = Field(
        default=True, description="Enable accessibility features"
    )


class AdaptiveLearningManager:
    """Step 1: Environment validation and adaptive learning orchestration (crawl_mcp.py methodology)."""

    def __init__(
        self,
        feedback_config: FeedbackCollectionConfig,
        learning_config: OnlineLearningConfig,
        personalization_config: PersonalizationConfig,
    ):
        """Initialize Adaptive Learning Manager with comprehensive validation."""
        self.feedback_config = feedback_config
        self.learning_config = learning_config
        self.personalization_config = personalization_config

        # Initialize paths
        self.data_dir = Path("data/adaptive_learning")
        self.models_dir = Path("models/adaptive_learning")
        self.feedback_dir = self.data_dir / "feedback"
        self.interactions_dir = self.data_dir / "interactions"
        self.personalization_dir = self.data_dir / "personalization"

        # Initialize components
        self.neo4j_client = None
        self.current_models = {}
        self.user_profiles = {}
        self.performance_metrics = {}

        # Step 1: Environment validation first
        self._validate_environment()
        self._initialize_directories()
        self._load_system_state()

    def _validate_environment(self) -> bool:
        """Step 1: Environment validation first (crawl_mcp.py methodology)."""
        try:
            # Check required environment variables
            required_vars = ["NEO4J_URI", "NEO4J_USER", "NEO4J_PASSWORD"]
            missing_vars = [var for var in required_vars if not os.getenv(var)]

            if missing_vars:
                logger.warning(f"Missing environment variables: {missing_vars}")

            # Check data directory permissions
            self.data_dir.mkdir(parents=True, exist_ok=True)
            if not os.access(self.data_dir, os.W_OK):
                raise AdaptiveLearningValidationError(
                    f"Data directory not writable: {self.data_dir}"
                )

            # Check models directory permissions
            self.models_dir.mkdir(parents=True, exist_ok=True)
            if not os.access(self.models_dir, os.W_OK):
                raise AdaptiveLearningValidationError(
                    f"Models directory not writable: {self.models_dir}"
                )

            logger.info("✅ Adaptive learning environment validation passed")
            return True

        except Exception as e:
            logger.error(f"❌ Environment validation failed: {e}")
            raise AdaptiveLearningValidationError(f"Environment validation failed: {e}")

    def _initialize_directories(self) -> None:
        """Initialize required directory structure."""
        directories = [
            self.data_dir,
            self.models_dir,
            self.feedback_dir,
            self.interactions_dir,
            self.personalization_dir,
            self.data_dir / "exports",
            self.data_dir / "metrics",
            self.models_dir / "active",
            self.models_dir / "archived",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"✅ Directory initialized: {directory}")

    def _load_system_state(self) -> None:
        """Load existing system state and configurations."""
        try:
            # Load user profiles
            profiles_file = self.personalization_dir / "user_profiles.json"
            if profiles_file.exists():
                with open(profiles_file) as f:
                    self.user_profiles = json.load(f)
                logger.info(f"✅ Loaded {len(self.user_profiles)} user profiles")

            # Load performance metrics
            metrics_file = self.data_dir / "metrics" / "performance_history.json"
            if metrics_file.exists():
                with open(metrics_file) as f:
                    self.performance_metrics = json.load(f)
                logger.info("✅ Loaded performance metrics history")

            # Load active models
            active_models_file = self.models_dir / "active_models.json"
            if active_models_file.exists():
                with open(active_models_file) as f:
                    self.current_models = json.load(f)
                logger.info(f"✅ Loaded {len(self.current_models)} active models")

        except Exception as e:
            logger.warning(f"⚠️ Failed to load system state: {e}")

    async def collect_user_feedback(
        self, user_id: str, interaction_id: str, feedback_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Step 2: Collect and validate user feedback (crawl_mcp.py methodology)."""
        try:
            # Step 2: Input validation
            if not user_id or not interaction_id:
                raise AdaptiveLearningValidationError(
                    "User ID and interaction ID are required"
                )

            if not isinstance(feedback_data, dict):
                raise AdaptiveLearningValidationError(
                    "Feedback data must be a dictionary"
                )

            # Validate feedback structure
            required_fields = ["rating", "content", "timestamp"]
            missing_fields = [
                field for field in required_fields if field not in feedback_data
            ]
            if missing_fields:
                raise AdaptiveLearningValidationError(
                    f"Missing required fields: {missing_fields}"
                )

            # Validate rating
            rating = feedback_data.get("rating")
            if not isinstance(rating, (int, float)) or not 0.0 <= rating <= 1.0:
                raise AdaptiveLearningValidationError(
                    "Rating must be a number between 0.0 and 1.0"
                )

            # Create feedback record
            feedback_record = {
                "feedback_id": f"feedback_{int(time.time())}_{user_id}",
                "user_id": user_id,
                "interaction_id": interaction_id,
                "timestamp": datetime.now().isoformat(),
                "rating": rating,
                "content": feedback_data.get("content", ""),
                "domain": feedback_data.get("domain"),
                "topic": feedback_data.get("topic"),
                "response_quality": feedback_data.get("response_quality"),
                "helpfulness": feedback_data.get("helpfulness"),
                "accuracy": feedback_data.get("accuracy"),
                "metadata": {
                    "collection_method": "api",
                    "anonymized": self.feedback_config.anonymization_enabled,
                    "system_version": "13.3",
                },
            }

            # Apply anonymization if enabled
            if self.feedback_config.anonymization_enabled:
                feedback_record["user_id"] = f"anon_{hash(user_id) % 10000}"

            # Save feedback
            result = await self._save_feedback_record(feedback_record)

            # Update user profile
            if self.personalization_config.user_profiles:
                await self._update_user_profile(user_id, feedback_record)

            # Trigger learning if threshold met
            if rating >= self.feedback_config.quality_threshold:
                await self._queue_for_learning(feedback_record)

            logger.info(f"✅ Feedback collected: {feedback_record['feedback_id']}")
            return {"success": True, "feedback_id": feedback_record["feedback_id"]}

        except Exception as e:
            logger.error(f"❌ Feedback collection failed: {e}")
            return {"success": False, "error": str(e)}

    async def _save_feedback_record(self, feedback_record: dict) -> dict[str, Any]:
        """Step 3: Save feedback with error handling (crawl_mcp.py methodology)."""
        try:
            # Save to daily feedback file
            date_str = datetime.now().strftime("%Y-%m-%d")
            feedback_file = self.feedback_dir / f"feedback_{date_str}.jsonl"

            with open(feedback_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(feedback_record) + "\n")

            # Save individual feedback file for processing
            individual_file = (
                self.feedback_dir / f"{feedback_record['feedback_id']}.json"
            )
            with open(individual_file, "w", encoding="utf-8") as f:
                json.dump(feedback_record, f, indent=2)

            return {"success": True, "file_path": str(feedback_file)}

        except Exception as e:
            logger.error(f"❌ Failed to save feedback: {e}")
            return {"success": False, "error": str(e)}

    async def _update_user_profile(self, user_id: str, feedback_record: dict) -> None:
        """Update user profile with feedback information."""
        try:
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = {
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    "experience_level": "intermediate",
                    "preferred_response_style": "detailed",
                    "domains_of_interest": [],
                    "feedback_history": [],
                    "performance_metrics": {
                        "average_rating": 0.0,
                        "total_interactions": 0,
                        "improvement_trend": "stable",
                    },
                }

            profile = self.user_profiles[user_id]

            # Update feedback history
            profile["feedback_history"].append(
                {
                    "feedback_id": feedback_record["feedback_id"],
                    "timestamp": feedback_record["timestamp"],
                    "rating": feedback_record["rating"],
                    "domain": feedback_record.get("domain"),
                }
            )

            # Keep only recent feedback (last 100 items)
            if len(profile["feedback_history"]) > 100:
                profile["feedback_history"] = profile["feedback_history"][-100:]

            # Update performance metrics
            ratings = [f["rating"] for f in profile["feedback_history"]]
            profile["performance_metrics"]["average_rating"] = sum(ratings) / len(
                ratings
            )
            profile["performance_metrics"]["total_interactions"] = len(ratings)

            # Update domains of interest
            domain = feedback_record.get("domain")
            if domain and domain not in profile["domains_of_interest"]:
                profile["domains_of_interest"].append(domain)

            # Save updated profiles
            profiles_file = self.personalization_dir / "user_profiles.json"
            with open(profiles_file, "w", encoding="utf-8") as f:
                json.dump(self.user_profiles, f, indent=2)

            logger.debug(f"✅ Updated user profile for {user_id}")

        except Exception as e:
            logger.warning(f"⚠️ Failed to update user profile: {e}")

    async def _queue_for_learning(self, feedback_record: dict) -> None:
        """Queue high-quality feedback for learning."""
        try:
            learning_queue_file = self.data_dir / "learning_queue.jsonl"

            queue_item = {
                "queued_at": datetime.now().isoformat(),
                "feedback_id": feedback_record["feedback_id"],
                "rating": feedback_record["rating"],
                "domain": feedback_record.get("domain"),
                "priority": "high" if feedback_record["rating"] >= 0.9 else "normal",
            }

            with open(learning_queue_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(queue_item) + "\n")

            logger.debug(
                f"✅ Queued feedback for learning: {feedback_record['feedback_id']}"
            )

        except Exception as e:
            logger.warning(f"⚠️ Failed to queue for learning: {e}")

    async def execute_incremental_learning(
        self, model_name: str, feedback_batch_size: int = None
    ) -> dict[str, Any]:
        """Step 4: Execute incremental learning process (crawl_mcp.py methodology)."""
        try:
            batch_size = feedback_batch_size or self.feedback_config.batch_size

            logger.info(f"🚀 Starting incremental learning for model: {model_name}")

            # Step 1: Collect learning data
            learning_data = await self._collect_learning_data(batch_size)
            if not learning_data["success"]:
                return learning_data

            # Step 2: Validate data quality
            validation_result = await self._validate_learning_data(
                learning_data["data"]
            )
            if not validation_result["success"]:
                return validation_result

            # Step 3: Execute incremental training
            training_result = await self._execute_incremental_training(
                model_name, learning_data["data"]
            )
            if not training_result["success"]:
                return training_result

            # Step 4: Validate model performance
            performance_result = await self._validate_model_performance(
                model_name, training_result["model_path"]
            )

            # Step 5: Deploy or rollback based on performance
            if (
                performance_result["success"]
                and performance_result["improvement"]
                >= self.learning_config.performance_threshold
            ):
                deployment_result = await self._deploy_updated_model(
                    model_name, training_result["model_path"]
                )

                logger.info("✅ Incremental learning completed successfully")
                return {
                    "success": True,
                    "model_name": model_name,
                    "training_samples": len(learning_data["data"]),
                    "performance_improvement": performance_result["improvement"],
                    "model_path": training_result["model_path"],
                    "deployment_status": deployment_result["status"],
                }
            else:
                # Rollback if performance didn't improve
                logger.warning("⚠️ Performance improvement insufficient, rolling back")
                return {
                    "success": False,
                    "error": "Performance improvement below threshold",
                    "improvement": performance_result.get("improvement", 0.0),
                    "threshold": self.learning_config.performance_threshold,
                }

        except Exception as e:
            logger.error(f"❌ Incremental learning failed: {e}")
            return {"success": False, "error": str(e)}

    async def _collect_learning_data(self, batch_size: int) -> dict[str, Any]:
        """Step 3: Collect learning data with error handling (crawl_mcp.py methodology)."""
        try:
            learning_queue_file = self.data_dir / "learning_queue.jsonl"
            if not learning_queue_file.exists():
                return {"success": False, "error": "No learning data available"}

            learning_items = []

            with open(learning_queue_file) as f:
                lines = f.readlines()

            # Process queue items
            for line in lines[:batch_size]:
                try:
                    queue_item = json.loads(line)
                    feedback_id = queue_item["feedback_id"]

                    # Load corresponding feedback
                    feedback_file = self.feedback_dir / f"{feedback_id}.json"
                    if feedback_file.exists():
                        with open(feedback_file) as f:
                            feedback_data = json.load(f)
                        learning_items.append(feedback_data)

                except json.JSONDecodeError:
                    continue

            if not learning_items:
                return {"success": False, "error": "No valid learning items found"}

            # Remove processed items from queue
            remaining_lines = lines[len(learning_items) :]
            with open(learning_queue_file, "w") as f:
                f.writelines(remaining_lines)

            logger.info(f"✅ Collected {len(learning_items)} learning items")
            return {"success": True, "data": learning_items}

        except Exception as e:
            logger.error(f"❌ Failed to collect learning data: {e}")
            return {"success": False, "error": str(e)}

    async def _validate_learning_data(self, learning_data: list) -> dict[str, Any]:
        """Validate learning data quality and consistency."""
        try:
            if not learning_data:
                return {"success": False, "error": "No learning data provided"}

            # Check data quality
            high_quality_items = [
                item
                for item in learning_data
                if item.get("rating", 0.0) >= self.feedback_config.quality_threshold
            ]

            if len(high_quality_items) < len(learning_data) * 0.8:
                return {
                    "success": False,
                    "error": f"Insufficient high-quality data: {len(high_quality_items)}/{len(learning_data)}",
                }

            logger.info(
                f"✅ Learning data validation passed: {len(high_quality_items)} high-quality items"
            )
            return {"success": True, "validated_items": len(high_quality_items)}

        except Exception as e:
            logger.error(f"❌ Learning data validation failed: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_incremental_training(
        self, model_name: str, learning_data: list
    ) -> dict[str, Any]:
        """Execute incremental training process (placeholder implementation)."""
        try:
            start_time = time.time()

            # Create new model version directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_version_dir = self.models_dir / f"{model_name}_v{timestamp}"
            model_version_dir.mkdir(exist_ok=True)

            # Simulate training process
            logger.info(f"🏋️ Training model with {len(learning_data)} samples...")

            # In a real implementation, this would:
            # 1. Load existing model
            # 2. Prepare training data from feedback
            # 3. Execute incremental fine-tuning
            # 4. Save updated model weights

            training_time = time.time() - start_time

            # Save training metadata
            metadata = {
                "model_name": model_name,
                "training_type": "incremental",
                "training_samples": len(learning_data),
                "training_time": training_time,
                "timestamp": datetime.now().isoformat(),
                "base_model": "llama3.1-8b",
                "performance_metrics": {
                    "training_loss": 0.15,  # Simulated
                    "validation_accuracy": 0.92,  # Simulated
                },
            }

            with open(model_version_dir / "training_metadata.json", "w") as f:
                json.dump(metadata, f, indent=2)

            logger.info(f"✅ Incremental training completed in {training_time:.2f}s")
            return {
                "success": True,
                "model_path": str(model_version_dir),
                "training_time": training_time,
                "samples_processed": len(learning_data),
            }

        except Exception as e:
            logger.error(f"❌ Incremental training failed: {e}")
            return {"success": False, "error": str(e)}

    async def _validate_model_performance(
        self, model_name: str, model_path: str
    ) -> dict[str, Any]:
        """Validate model performance improvement."""
        try:
            # Simulate performance validation
            # In a real implementation, this would:
            # 1. Load validation dataset
            # 2. Run inference on both old and new models
            # 3. Compare performance metrics
            # 4. Calculate improvement percentage

            # Simulated performance improvement
            baseline_accuracy = 0.85
            new_accuracy = 0.89
            improvement = (new_accuracy - baseline_accuracy) / baseline_accuracy

            logger.info(f"📊 Performance validation: {improvement:.1%} improvement")
            return {
                "success": True,
                "improvement": improvement,
                "baseline_accuracy": baseline_accuracy,
                "new_accuracy": new_accuracy,
            }

        except Exception as e:
            logger.error(f"❌ Performance validation failed: {e}")
            return {"success": False, "error": str(e)}

    async def _deploy_updated_model(
        self, model_name: str, model_path: str
    ) -> dict[str, Any]:
        """Deploy updated model with version management."""
        try:
            # Update active models registry
            self.current_models[model_name] = {
                "model_path": model_path,
                "deployment_timestamp": datetime.now().isoformat(),
                "status": "active",
                "version": Path(model_path).name,
            }

            # Save active models registry
            active_models_file = self.models_dir / "active_models.json"
            with open(active_models_file, "w") as f:
                json.dump(self.current_models, f, indent=2)

            logger.info(f"🚀 Model deployed successfully: {model_name}")
            return {"success": True, "status": "deployed"}

        except Exception as e:
            logger.error(f"❌ Model deployment failed: {e}")
            return {"success": False, "error": str(e)}

    @asynccontextmanager
    async def managed_adaptive_learning(self) -> AsyncGenerator[dict[str, Any], None]:
        """Step 6: Managed adaptive learning context with resource cleanup (crawl_mcp.py methodology)."""
        resources = {"neo4j_client": None, "active_models": {}, "monitoring": None}

        try:
            logger.info("🚀 Initializing adaptive learning resources...")

            # Initialize Neo4j connection
            if self._check_neo4j_connection():
                from src.ignition.graph.client import IgnitionGraphClient

                resources["neo4j_client"] = IgnitionGraphClient()
                resources["neo4j_client"].connect()

            # Load active models
            resources["active_models"] = self.current_models.copy()

            # Initialize monitoring
            resources["monitoring"] = {"start_time": time.time(), "status": "active"}

            yield resources

        except Exception as e:
            logger.error(f"❌ Adaptive learning initialization failed: {e}")
            raise AdaptiveLearningValidationError(f"Adaptive learning failed: {e}")
        finally:
            # Step 6: Cleanup resources
            await self._cleanup_adaptive_learning_resources(resources)

    async def _cleanup_adaptive_learning_resources(
        self, resources: dict[str, Any]
    ) -> None:
        """Clean up adaptive learning resources."""
        try:
            logger.info("🧹 Cleaning up adaptive learning resources...")

            # Cleanup Neo4j connection
            if resources.get("neo4j_client"):
                resources["neo4j_client"].disconnect()

            # Save final state
            await self._save_system_state()

            logger.info("✅ Adaptive learning resources cleaned up")

        except Exception as e:
            logger.warning(f"⚠️ Resource cleanup warning: {e}")

    async def _save_system_state(self) -> None:
        """Save current system state to persistent storage."""
        try:
            # Save user profiles
            profiles_file = self.personalization_dir / "user_profiles.json"
            with open(profiles_file, "w", encoding="utf-8") as f:
                json.dump(self.user_profiles, f, indent=2)

            # Save performance metrics
            metrics_file = self.data_dir / "metrics" / "performance_history.json"
            with open(metrics_file, "w", encoding="utf-8") as f:
                json.dump(self.performance_metrics, f, indent=2)

            # Save active models
            active_models_file = self.models_dir / "active_models.json"
            with open(active_models_file, "w", encoding="utf-8") as f:
                json.dump(self.current_models, f, indent=2)

            logger.debug("✅ System state saved successfully")

        except Exception as e:
            logger.warning(f"⚠️ Failed to save system state: {e}")

    def _check_neo4j_connection(self) -> bool:
        """Check Neo4j connection availability."""
        try:
            from src.ignition.graph.client import IgnitionGraphClient

            test_client = IgnitionGraphClient()
            if test_client.connect():
                test_client.disconnect()
                return True
            return False
        except Exception:
            return False

    async def get_adaptive_learning_status(self) -> dict[str, Any]:
        """Get comprehensive adaptive learning system status."""
        try:
            logger.info("📊 Gathering adaptive learning status...")

            # Environment status
            env_status = {
                "neo4j_available": self._check_neo4j_connection(),
                "data_directory_writable": os.access(self.data_dir, os.W_OK),
                "models_directory_writable": os.access(self.models_dir, os.W_OK),
                "feedback_collection_enabled": self.feedback_config.collection_enabled,
                "incremental_learning_enabled": self.learning_config.incremental_updates,
                "personalization_enabled": self.personalization_config.user_profiles,
            }

            # System metrics
            system_metrics = {
                "total_user_profiles": len(self.user_profiles),
                "active_models": len(self.current_models),
                "feedback_files": len(list(self.feedback_dir.glob("*.json"))),
                "learning_queue_size": self._get_learning_queue_size(),
                "data_retention_days": self.feedback_config.retention_days,
            }

            # Configuration
            config_status = {
                "feedback_config": self.feedback_config.dict(),
                "learning_config": self.learning_config.dict(),
                "personalization_config": self.personalization_config.dict(),
            }

            return {
                "success": True,
                "environment": env_status,
                "metrics": system_metrics,
                "configuration": config_status,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Status gathering failed: {e}")
            return {"success": False, "error": f"Status gathering failed: {e}"}

    def _get_learning_queue_size(self) -> int:
        """Get current learning queue size."""
        try:
            learning_queue_file = self.data_dir / "learning_queue.jsonl"
            if learning_queue_file.exists():
                with open(learning_queue_file) as f:
                    return len(f.readlines())
            return 0
        except Exception:
            return 0
