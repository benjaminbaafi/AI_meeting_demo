"""
Quick script to test Redis connection and check for keys.
Run this to verify Redis is working and has data.
"""
import asyncio
import sys
from utils.redis_service import get_redis_service


async def test_redis():
    """Test Redis connection and list keys."""
    try:
        print("Connecting to Redis...")
        redis_service = await get_redis_service()
        
        # Get the Redis client
        client = redis_service.redis_client
        if not client:
            print("❌ Redis client not available")
            return
        
        # Test connection
        await client.ping()
        print("✅ Redis connection successful!\n")
        
        # Scan for job keys
        print("Scanning for job keys (pattern: job:*)...")
        job_keys = []
        cursor = 0
        pattern = "job:*"
        
        while True:
            cursor, keys = await client.scan(cursor, match=pattern, count=100)
            job_keys.extend(keys)
            if cursor == 0:
                break
        
        # Decode keys
        decoded_keys = [
            k.decode('utf-8') if isinstance(k, bytes) else k
            for k in job_keys
        ]
        
        print(f"\n📊 Found {len(decoded_keys)} job key(s)")
        
        if decoded_keys:
            print("\n🔑 Job Keys:")
            for key in decoded_keys[:20]:  # Show first 20
                print(f"  - {key}")
            if len(decoded_keys) > 20:
                print(f"  ... and {len(decoded_keys) - 20} more")
        else:
            print("\n⚠️  No job keys found!")
            print("\n💡 To create test data:")
            print("   1. Start your server: uv run python app.py")
            print("   2. Go to http://localhost:8000/docs")
            print("   3. Upload a video/audio file via POST /api/v1/upload")
            print("   4. Then check Redis Desktop Manager again")
        
        # Check all keys (not just jobs)
        print("\n📋 Checking all keys in database...")
        all_keys = []
        cursor = 0
        
        while True:
            cursor, keys = await client.scan(cursor, count=100)
            all_keys.extend(keys)
            if cursor == 0:
                break
        
        decoded_all = [
            k.decode('utf-8') if isinstance(k, bytes) else k
            for k in all_keys
        ]
        
        print(f"Total keys in database: {len(decoded_all)}")
        
        if decoded_all:
            print("\nAll keys:")
            for key in decoded_all[:30]:  # Show first 30
                print(f"  - {key}")
            if len(decoded_all) > 30:
                print(f"  ... and {len(decoded_all) - 30} more")
        
        # Get database info
        info = await client.info()
        print(f"\n📈 Database Info:")
        print(f"  - Redis Version: {info.get('redis_version', 'unknown')}")
        print(f"  - Used Memory: {info.get('used_memory_human', 'unknown')}")
        print(f"  - Connected Clients: {info.get('connected_clients', 0)}")
        print(f"  - Total Keys: {info.get('db0', {}).get('keys', 0) if 'db0' in info else 'unknown'}")
        
        # Close connection
        await redis_service.disconnect()
        print("\n✅ Test complete!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure Redis is running: redis-cli ping")
        print("2. Check your .env file has correct REDIS_URL")
        print("3. Verify Redis is accessible on localhost:6379")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(test_redis())

